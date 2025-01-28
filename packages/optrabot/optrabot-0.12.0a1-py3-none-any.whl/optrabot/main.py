import asyncio
from contextlib import asynccontextmanager
import inspect
from fastapi import FastAPI, BackgroundTasks
import logging
from loguru import logger
import optrabot.config as optrabotcfg
from .optrabot import OptraBot
import uvicorn
import sys
import argparse

ValidLogLevels = ['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR']

@asynccontextmanager
async def lifespan(app: FastAPI):
	app.optraBot = OptraBot(app)
	await app.optraBot.startup()
	yield
	await app.optraBot.shutdown()

"""fix yelling at me error"""
from functools import wraps
 
from asyncio.proactor_events import _ProactorBasePipeTransport
 
def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper
 
_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
"""fix yelling at me error end"""

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
	return "Welcome to OptraBot"


class InterceptHandler(logging.Handler):
	def emit(self, record: logging.LogRecord) -> None:
		if not record.name.startswith('apscheduler'):
			return
			#logger.debug(record.getMessage())
		# Get corresponding Loguru level if it exists.
		level: str | int
		try:
			level = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		# Find caller from where originated the logged message.
		frame, depth = inspect.currentframe(), 0
		while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
			frame = frame.f_back
			depth += 1
		level = 'DEBUG' if level == 'INFO' else level
		logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def configureLogging(requestedLogLevel, logScheduler):
	loglevel = 'INFO'
	if requestedLogLevel not in ValidLogLevels and requestedLogLevel != None:
		print(f'Log Level {requestedLogLevel} is not valid!')
	elif requestedLogLevel != None:
		loglevel = requestedLogLevel
	
	logFormat = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> |"
	if loglevel == 'DEBUG':
		logFormat += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
	logFormat += "<level>{message}</level>"

	logger.remove()
	logger.add(sys.stderr, level=loglevel, format = logFormat)
	logger.add("optrabot.log", level='DEBUG', format = logFormat, rotation="5 MB", retention="10 days")

	if logScheduler:
		logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
	#logging.basicConfig(level=logging.ERROR)  # Stummschalten aller Standard-Logger
		apscheduler_logger = logging.getLogger('apscheduler')
		apscheduler_logger.setLevel(loglevel)
	#handler = logging.StreamHandler(sys.stdout)
	#handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
	#apscheduler_logger.addHandler(handler)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--loglevel", help="Log Level", choices=ValidLogLevels)
	parser.add_argument("--logscheduler", help="Log Job Scheduler", action="store_true")
	args = parser.parse_args()
	configureLogging(args.loglevel, args.logscheduler)
	
	if optrabotcfg.ensureInitialConfig()	== True:
		# Get web port from config
		configuration = optrabotcfg.Config("config.yaml")
		if configuration.loaded == False:
			print("Configuration error. Unable to run OptraBot!")
			sys.exit(1)
		webPort: int
		try:
			webPort = configuration.get('general.port')
		except KeyError as keyErr:
			webPort = 8080
		uvicorn.run("optrabot.main:app", port=int(webPort), log_level="info")
	else:
		print("Configuration error. Unable to run OptraBot!")