from asyncio import sleep

from fastapi import FastAPI, Request
from elastic_structlog import configure_es_structlog_logger, get_structlog_logger
from tests.models.user_model import User
from tests.service_test import service_error
from structlog.contextvars import bind_contextvars, clear_contextvars

configure_es_structlog_logger(
    host="http://20.93.143.180:9200",
    basic_auth=("elastic", "soD2v7cv3bNI+XZGJlpA"),
    index="structlog_es_example",
    flush_frequency=5,
    verify_certs=False,
    raise_on_indexing_error=True
)

app = FastAPI()

logger = get_structlog_logger()

user_model = User(username="nuriel", email="omerugly@gmail.com")


@app.middleware("http")
async def clear_contextvars_middleware(request: Request, call_next):
    clear_contextvars()
    return await call_next(request)


@app.get("/")
async def root():
    try:
        bind_contextvars(name="nuriel")
        logger.info("Hi this is message from ROOT", user=user_model)
        await sleep(5)
        service_error()
        return "Hello From Root!"
    except Exception as e:
        logger.error("ERROR!!!!", exc_info=e)


@app.get("/second")
async def second():
    try:
        bind_contextvars(name="ido")
        logger.info("Hi this is message from SECOND")
        return "Hello From Second!"
    except Exception as e:
        logger.error("ERROR!!!!", exc_info=e)
