import datetime as _datetime
from threading import Lock as _Lock, Timer as _Timer
from elasticsearch import Elasticsearch as _Elasticsearch
from elasticsearch import helpers as _es_helpers
import copy

from elastic_structlog.elastic_structlog_serializer import ElasticStructLogSerializer

_MAX_BUFFER_SIZE: int = 1000


class ESStructLogExtension:
    def __init__(self,
                 host: str,
                 basic_auth: tuple[str, str],
                 index: str,
                 flush_frequency: int = 1,
                 raise_on_indexing_error: bool = False,
                 verify_certs: bool = True):
        """Extension Constructor

        :param host: The host of the elasticsearch.
        :type host: str
        :param basic_auth: The basic auth tuple to elastic.
        :type basic_auth: tuple
        :param index: The elastic index name.
        :type index: str
        :param flush_frequency: Frequency of flushing buffers.
        :type flush_frequency: int
        :param raise_on_indexing_error: Whether to raise an exception if indexing to elastic fails.
        :type raise_on_indexing_error: bool
        :param verify_certs: Whether to verify certificates.
        :type verify_certs: bool"""
        self._es_host = host
        self._es_basic_auth_cred = basic_auth
        self._es_index = index
        self._verify_certs = verify_certs
        self._flush_frequency_in_sec = flush_frequency
        self._raise_on_indexing_error = raise_on_indexing_error

        self._buffer = []
        self._lock = _Lock()
        self._timer: _Timer | None = None

        self._es_client = _Elasticsearch(hosts=self._es_host,
                                         http_auth=basic_auth,
                                         verify_certs=verify_certs,
                                         serializer=ElasticStructLogSerializer())

    def __get_daily_index_name(self):
        return f"{self._es_index}-{_datetime.datetime.now().strftime('%Y.%m.%d')}"

    def __schedule_flush(self):
        if self._timer is None:
            self._timer = _Timer(self._flush_frequency_in_sec, self.__flush)
            self._timer.daemon = True
            self._timer.start()

    def __flush(self):
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None

        if not self._buffer:
            return

        try:
            with self._lock:
                logs_buffer = self._buffer
                self._buffer = []

            actions = (
                {
                    '_index': self.__get_daily_index_name(),
                    '_source': dict(buffer_record)
                } for buffer_record in logs_buffer
            )
            _es_helpers.bulk(client=self._es_client, actions=actions, stats_only=True)

        except Exception as e:
            if self._raise_on_indexing_error:
                raise e

    def close(self):
        """Close the timer and flush buffers."""
        if self._timer is not None:
            self.__flush()
        self._timer = None

    def emit(self, record):
        """Emit a record.
        Adding the record to the buffer that will be flushed.

        :param record: The record to emit."""
        for key, value in dict(record).items():
            if key == "args":
                value = tuple(str(arg) for arg in value)
            record[key] = "" if value is None else value

        with self._lock:
            self._buffer.append(copy.deepcopy(record))

        if len(self._buffer) >= _MAX_BUFFER_SIZE:
            self.__flush()
        else:
            self.__schedule_flush()
