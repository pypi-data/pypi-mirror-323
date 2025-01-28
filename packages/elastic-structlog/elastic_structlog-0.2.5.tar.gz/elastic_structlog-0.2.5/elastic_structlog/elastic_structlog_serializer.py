from typing import Any
from elasticsearch.serializer import JsonSerializer


class ElasticStructLogSerializer(JsonSerializer):
    """Wrapping the default elastic serializer. But when TypeError Exception raised, the data converted to string"""
    def default(self, data: Any) -> Any:
        try:
            return super(ElasticStructLogSerializer, self).default(data)
        except TypeError:
            return str(data)
