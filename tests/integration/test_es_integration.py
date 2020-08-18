import pytest
from elasticsearch import Elasticsearch
from essnapshot.es import connection_check, ensure_snapshot_repo
from essnapshot.es import create_snapshot, get_snapshots, delete_snapshots
from essnapshot.es import initialize_es_client
from essnapshot.helpers import open_configfile
from time import sleep


@pytest.fixture
def repo_diff_configuration():
    return {
            "type": "fs",
            "settings": {
                "location": "/mnt/snapshot",
                "compress": "false"
            }
        }


esclients = {
    'es7client': Elasticsearch("localhost:9200"),
    'es6client': Elasticsearch("localhost:9201")
}


def is_responsive():
    online = []
    for esclient in esclients.values():
        online.append(esclient.ping())
        if False in online:
            return False
        else:
            return True


@pytest.fixture(scope="session")
def es_service(docker_ip, docker_services):
    """Ensure that ES services is up and responsive."""
    docker_services.wait_until_responsive(
        timeout=60.0, pause=1.0, check=lambda: is_responsive()
    )
    return open_configfile('tests/configs/integration.yaml')


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_initialize_es_client(es_service, esclient):
    testclient = initialize_es_client(es_service['es_connections'])
    assert testclient.ping()


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_connection_check(es_service, esclient):
    assert connection_check(esclients[esclient])


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_ensure_snapshot_repo(es_service, esclient):
    ensure_snapshot_repo(
        esclients[esclient],
        es_service['repository_name'],
        es_service['repository'])
    repo = esclients[esclient].snapshot.get_repository(
        repository=es_service['repository_name'])
    assert es_service['repository_name'] in repo
    assert repo[es_service['repository_name']] == es_service['repository']


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_ensure_snapshot_repo_warn_configdiff(
        es_service,
        esclient,
        repo_diff_configuration,
        capsys):
    ensure_snapshot_repo(
        esclients[esclient],
        es_service['repository_name'],
        es_service['repository'])
    ensure_snapshot_repo(
        esclients[esclient],
        es_service['repository_name'],
        repo_diff_configuration
    )
    captured = capsys.readouterr()
    assert captured.err == (
        "WARNING: Snapshot repo '{r}' configuration "
        "differs from configfile.\n").format(r=es_service['repository_name'])


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_create_snapshot(es_service, esclient):
    assert create_snapshot(
        esclients[esclient],
        es_service['repository_name'],
        'integration_create')
    assert esclients[esclient].snapshot.get(
        es_service['repository_name'],
        snapshot='integration_create')


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_get_snapshots(es_service, esclient):
    esclients[esclient].snapshot.create(
        repository=es_service['repository_name'],
        snapshot='integration_list')
    snaplist = get_snapshots(esclients[esclient],
                             es_service['repository_name'])
    assert isinstance(snaplist, list)
    assert len([s for s in snaplist if s['id'] == 'integration_list']) > 0


@pytest.mark.integration_test
@pytest.mark.parametrize('esclient',
                         esclients.keys())
def test_delete_snapshots(es_service, esclient):
    assert esclients[esclient].snapshot.create(
        repository=es_service['repository_name'],
        snapshot='integration_delete')
    sleep(1)
    assert delete_snapshots(
        esclients[esclient],
        es_service['repository_name'],
        ['integration_delete'])
    # pylint: disable=unexpected-keyword-arg
    sl = esclients[esclient].cat.snapshots(
        repository=es_service['repository_name'],
        format='json')
    assert len([s for s in sl if s['id'] == 'integration_delete']) < 1
