import pytest
from essnapshot.es import initialize_es_client
import elasticsearch


def test_initialize_es_client_default():
    assert isinstance(initialize_es_client(None), elasticsearch.client.Elasticsearch)


def test_initialize_es_client_with_params():
#    with pytest.raises(TypeError):
    es_connections = [
        {
            'host': 'localhost',
            'port': '9200',
        }
    ]
    assert isinstance(initialize_es_client(es_connections), elasticsearch.client.Elasticsearch)
