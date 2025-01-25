import asyncio
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import Lock
from typing import Any, Dict, Optional

import psutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from browser_use import Agent

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a rotating file handler (10MB per file, keep 5 backup files)
file_handler = RotatingFileHandler(
	os.path.join(LOGS_DIR, 'agent_manager.log'),
	maxBytes=10 * 1024 * 1024,  # 10MB
	backupCount=5,
	encoding='utf-8',
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Create a separate file for agent-specific logs
agent_file_handler = RotatingFileHandler(
	os.path.join(LOGS_DIR, 'agents.log'),
	maxBytes=10 * 1024 * 1024,  # 10MB
	backupCount=5,
	encoding='utf-8',
)
agent_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Create a queue for real-time log messages
log_queue = Queue()
log_lock = Lock()


class LogHandler(logging.Handler):
	def emit(self, record):
		log_entry = self.format(record)
		with log_lock:
			log_queue.put(log_entry)


# Add handlers to the browser_use logger
browser_use_logger = logging.getLogger('browser_use')
browser_use_logger.addHandler(LogHandler())
browser_use_logger.addHandler(agent_file_handler)

app = FastAPI()

# Enable CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],  # Allows all origins
	allow_credentials=True,
	allow_methods=['*'],  # Allows all methods
	allow_headers=['*'],  # Allows all headers
)

# Create static directory if it doesn't exist
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

# Serve static files
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


class TaskRequest(BaseModel):
	agent_id: str
	task: str


class AgentManager:
	def __init__(self):
		self.agents: Dict[str, Dict[str, Any]] = {}
		self.max_agents = 40  # Increased to 100 agents
		self._lock = asyncio.Lock()
		self.process = psutil.Process()
		self.start_time = time.time()
		logger.info(f'AgentManager initialized with max_agents={self.max_agents}')

	async def create_agent(self, agent_id: str, task: str):
		async with self._lock:
			if len(self.agents) >= self.max_agents:
				current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
				logger.error(f'Max agents reached. Current memory usage: {current_memory:.2f}MB')
				raise ValueError(f'Maximum number of agents ({self.max_agents}) reached. Memory usage: {current_memory:.2f}MB')

			if agent_id in self.agents:
				logger.warning(f'Agent {agent_id} already exists')
				raise ValueError(f'Agent {agent_id} already exists')

			try:
				llm = ChatOpenAI(model='gpt-4o-mini')
				agent = {
					'instance': Agent(task=task, llm=llm),
					'task': task,
					'running': False,
					'created_at': time.time(),
					'last_active': time.time(),
				}
				self.agents[agent_id] = agent
				logger.info(f'Created agent {agent_id}. Total agents: {len(self.agents)}')
			except Exception as e:
				logger.error(f'Failed to create agent {agent_id}: {str(e)}')
				raise

	def get_system_stats(self) -> dict:
		stats = {
			'total_agents': len(self.agents),
			'memory_usage_mb': self.process.memory_info().rss / 1024 / 1024,
			'cpu_percent': self.process.cpu_percent(),
			'uptime_seconds': time.time() - self.start_time,
			'thread_count': self.process.num_threads(),
		}
		logger.info(f'System stats: {stats}')
		return stats

	def get_agent(self, agent_id: str) -> Agent:
		if agent_id not in self.agents:
			raise ValueError(f'Agent {agent_id} not found')
		return self.agents[agent_id]['instance']

	def get_agent_status(self, agent_id: str):
		if agent_id not in self.agents:
			return 'not_created'

		agent_data = self.agents[agent_id]
		agent = agent_data['instance']

		if agent._stopped:
			return 'stopped'
		elif agent._paused:
			return 'paused'
		elif agent_data['running']:
			return 'running'
		return 'ready'

	def set_running(self, agent_id: str, value: bool):
		if agent_id in self.agents:
			self.agents[agent_id]['running'] = value

	def list_agents(self):
		return {
			agent_id: {'task': data['task'], 'status': self.get_agent_status(agent_id)} for agent_id, data in self.agents.items()
		}


# Create a singleton instance
agent_manager = AgentManager()


@app.get('/')
async def read_root():
	return FileResponse(os.path.join(STATIC_DIR, 'index.html'))


@app.post('/agent/run')
async def run_agent(request: TaskRequest):
	try:
		start_time = time.time()
		if request.agent_id not in agent_manager.agents:
			await agent_manager.create_agent(request.agent_id, request.task)

		agent = agent_manager.get_agent(request.agent_id)
		agent_manager.set_running(request.agent_id, True)

		# Run in background task to not block
		task = asyncio.create_task(agent.run())

		# Add completion callback for debugging
		def done_callback(future):
			try:
				future.result()
			except Exception as e:
				logger.error(f'Agent {request.agent_id} failed: {str(e)}')
			finally:
				agent_manager.set_running(request.agent_id, False)

		task.add_done_callback(done_callback)

		setup_time = time.time() - start_time
		return {
			'status': 'running',
			'agent_id': request.agent_id,
			'task': request.task,
			'setup_time_ms': setup_time * 1000,
			'total_agents': len(agent_manager.agents),
		}
	except Exception as e:
		logger.error(f'Error running agent {request.agent_id}: {str(e)}')
		raise HTTPException(status_code=400, detail=str(e))


@app.get('/ping')
async def ping():
	return {'status': 'ok'}


@app.post('/agent/{agent_id}/pause')
async def pause_agent(agent_id: str):
	try:
		agent = agent_manager.get_agent(agent_id)
		agent.pause()
		return {'status': 'paused', 'agent_id': agent_id}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@app.post('/agent/{agent_id}/resume')
async def resume_agent(agent_id: str):
	try:
		agent = agent_manager.get_agent(agent_id)
		agent.resume()
		return {'status': 'resumed', 'agent_id': agent_id}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@app.post('/agent/{agent_id}/stop')
async def stop_agent(agent_id: str):
	try:
		agent = agent_manager.get_agent(agent_id)
		agent.stop()
		agent_manager.set_running(agent_id, False)
		return {'status': 'stopped', 'agent_id': agent_id}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@app.get('/agent/{agent_id}/status')
async def get_agent_status(agent_id: str):
	try:
		status = agent_manager.get_agent_status(agent_id)
		task = agent_manager.agents[agent_id]['task'] if agent_id in agent_manager.agents else None
		return {'status': status, 'agent_id': agent_id, 'task': task}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@app.get('/agents')
async def list_agents():
	return agent_manager.list_agents()


@app.get('/logs')
async def event_stream():
	async def generate():
		while True:
			if not log_queue.empty():
				with log_lock:
					while not log_queue.empty():
						log_entry = log_queue.get()
						yield {'event': 'log', 'data': log_entry}
			await asyncio.sleep(0.1)

	return EventSourceResponse(generate())


@app.get('/system/stats')
async def get_system_stats():
	return agent_manager.get_system_stats()


if __name__ == '__main__':
	import uvicorn

	uvicorn.run(app, host='0.0.0.0', port=8000)
