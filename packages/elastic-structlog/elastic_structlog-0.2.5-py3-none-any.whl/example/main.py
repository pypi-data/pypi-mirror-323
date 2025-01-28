import structlog
from fastapi import FastAPI, Request, Depends
import elastic_structlog
from elastic_structlog import ESStructLogExtension


# Suggesting to read the structlog documentation in order to understand how to use it:
# https://www.structlog.org/en/stable/getting-started.html#installation

# If you want to configure the structlog library by yourself,
# but still have the option to send directly to Elastic, do this:
def manual_structlog_configure():
    # First create ESStructLogExtension instance.
    es_extension = ESStructLogExtension(
        host="http://20.93.143.180:9200",
        basic_auth=("elastic", "soD2v7cv3bNI+XZGJlpA"),
        index="structlog_es_example",
        flush_frequency=5,
        raise_on_indexing_error=False,
        verify_certs=False
    )

    # Second, configure the structlog - use directly the original module of structlog.
    # Notice how you should use the processor that the package offers:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            elastic_structlog.elastic_processor.ESStructLogProcessor(es_extension=es_extension),
            structlog.processors.KeyValueRenderer()
        ]
    )


app = FastAPI()

# Or, you can use the function 'configure_es_structlog_logger' that the module offers.
elastic_structlog.elastic_processor.configure_es_structlog_logger(
    host="http://20.93.143.180:9200",
    basic_auth=("elastic", "soD2v7cv3bNI+XZGJlpA"),
    index="structlog_es_example",
    flush_frequency=5,
    verify_certs=False,
)


# In order to make sure we use the package as we expect, create a middleware
# that runs before every route - which clearing the contextual vars from the logger's event_dict
@app.middleware("http")
async def clear_old_context(request: Request, call_next):
    structlog.contextvars.clear_contextvars()
    return await call_next(request)


# Inject the logger using the built-in function of structlog
# (suggesting to use the function from '' in order to get type hinting):
@app.get("/")
async def root(logger: structlog.stdlib.BoundLogger = Depends(elastic_structlog.elastic_processor.get_structlog_logger)):
    try:
        structlog.contextvars.bind_contextvars(user_name="omer_is_ugly")
        logger.info("Hello from LOGGER!", is_eldad_ugly_as_well=True)
        # OUTPUT: { "message": "Hello from LOGGER!", "user_name": "omer_is_ugly", "is_eldad_ugly_as_well: true }
    except Exception as e:
        logger.error("bye", exc_info=e)
        return {"message": "Hello World"}
