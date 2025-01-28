import uuid
import structlog
from structlog.typing import EventDict
from .elastic_extension import ESStructLogExtension
from structlog.contextvars import bind_contextvars

_ES_MESSAGE_KEY = "message"
_ISO_FORMAT = "iso"
_REQUEST_ID_KEY = "request_id"


class ESStructLogProcessor:
    def __init__(self, es_extension: ESStructLogExtension = None):
        """Elastic Processor for structlog.

        :param es_extension: Configured ES extension for processor."""
        self._es_struct_log_extension = es_extension

    def __call__(self, _logger, _name, event_dict: EventDict):
        if event_dict.get(_REQUEST_ID_KEY, None) is None:
            generated_request_id = str(uuid.uuid4())
            bind_contextvars(request_id=generated_request_id)
            event_dict[_REQUEST_ID_KEY] = generated_request_id
        self._es_struct_log_extension.emit(event_dict)

        return event_dict


def configure_es_structlog_logger(host: str,
                                  basic_auth: tuple[str, str],
                                  index: str,
                                  flush_frequency: int,
                                  verify_certs: bool = True,
                                  raise_on_indexing_error: bool = False):
    """Default configuration for structlog & ES processor.
    
    :param raise_on_indexing_error: If it should raise an Exception when indexing error is raised.
    :param flush_frequency: Frequency of flushing log messages sent to Elastic.
    :param verify_certs: Should certificates be verified?
    :param index: Elasticsearch index name.
    :param basic_auth: Elastic user credentials.
    :param host: The Elastic host to connect to. 
    """""
    processors = [
        structlog.processors.CallsiteParameterAdder(parameters=[structlog.processors.CallsiteParameter.MODULE,
                                                                structlog.processors.CallsiteParameter.FUNC_NAME,
                                                                structlog.processors.CallsiteParameter.FILENAME]),
        structlog.contextvars.merge_contextvars,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt=_ISO_FORMAT),
        structlog.processors.EventRenamer(_ES_MESSAGE_KEY),
        ESStructLogProcessor(es_extension=ESStructLogExtension(host=host,
                                                               basic_auth=basic_auth,
                                                               index=index,
                                                               flush_frequency=flush_frequency,
                                                               verify_certs=verify_certs,
                                                               raise_on_indexing_error=raise_on_indexing_error)),
        structlog.processors.KeyValueRenderer(key_order=["message", "request_id"])
    ]

    structlog.configure(
        processors=processors,
        context_class=dict
    )


def get_structlog_logger() -> structlog.stdlib.BoundLogger:
    """Function that return the structlog default logger. Use it for dependency injection."""
    logger = structlog.stdlib.get_logger()
    if not structlog.is_configured():
        logger.warning("STRUCTLOG IS NOT CONFIGURED! Make sure to configure structlog!")

    return structlog.stdlib.get_logger()
