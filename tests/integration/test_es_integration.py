import pytest
from elasticsearch import Elasticsearch
from essnapshot.es import connection_check, ensure_snapshot_repo
from essnapshot.es import create_snapshot, get_snapshots, delete_snapshots
from essnapshot.es import initialize_es_client
from essnapshot.helpers import open_configfile
from time import sleep

esclient = Elasticsearch()


def is_responsive():
    if esclient.ping():
        return True
    else:
        return False


@pytest.fixture(scope="session")
def es_service(docker_ip, docker_services):
    """Ensure that ES service is up and responsive."""
    docker_services.wait_until_responsive(
        timeout=60.0, pause=1.0, check=lambda: is_responsive()
    )
    return open_configfile('tests/configs/integration.yaml')


@pytest.mark.integration_test
def test_initialize_es_client(es_service):
    testclient = initialize_es_client(es_service['es_connections'])
    assert testclient.ping()


@pytest.mark.integration_test
def test_connection_check(es_service):
    assert connection_check(esclient)


@pytest.mark.integration_test
def test_ensure_snapshot_repo(es_service):
    ensure_snapshot_repo(
        esclient,
        es_service['repository_name'],
        es_service['repository'])
    repo = esclient.snapshot.get_repository(
        repository=es_service['repository_name'])
    assert es_service['repository_name'] in repo
    assert repo[es_service['repository_name']] == es_service['repository']


@pytest.mark.integration_test
def test_create_snapshot(es_service):
    assert create_snapshot(
        esclient,
        es_service['repository_name'],
        'integration_create')
    assert esclient.snapshot.get(
        es_service['repository_name'],
        snapshot='integration_create')


@pytest.mark.integration_test
def test_get_snapshots(es_service):
    esclient.snapshot.create(
        repository=es_service['repository_name'],
        snapshot='integration_list')
    snaplist = get_snapshots(esclient, es_service['repository_name'])
    assert isinstance(snaplist, list)
    assert len([s for s in snaplist if s['id'] == 'integration_list']) > 0


@pytest.mark.integration_test
def test_delete_snapshots(es_service):
    assert esclient.snapshot.create(
        repository=es_service['repository_name'],
        snapshot='integration_delete')
    sleep(1)
    assert delete_snapshots(
        esclient,
        es_service['repository_name'],
        ['integration_delete'])
    # pylint: disable=unexpected-keyword-arg
    sl = esclient.cat.snapshots(
        repository=es_service['repository_name'],
        format='json')
    assert len([s for s in sl if s['id'] == 'integration_delete']) < 1
