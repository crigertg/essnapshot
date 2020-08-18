import sys
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch import TransportError, ConnectionError


def initialize_es_client(es_connections: list):
    """initialize an instance of the ES client and return it."""
    return Elasticsearch(es_connections)


def connection_check(esclient):
    """Make sure that the connection to the ES cluster is working"""
    if not esclient.ping():
        print("Can't connect to ES Cluster.", file=sys.stderr)
        try:
            esclient.cluster.health()
        except ConnectionError as e:
            print(e, file=sys.stderr)
            exit(1)
    return True


def ensure_snapshot_repo(
        esclient,
        repository_name: str,
        repository_config: dict):
    """Check if snapshot repo exists, if not, create it."""
    try:
        snapshot_repo = esclient.snapshot.get_repository(
            repository=repository_name)
        if not snapshot_repo[repository_name] == repository_config:
            print("WARNING: Snapshot repo '{r}' configuration differs from "
                  "configfile.".format(r=repository_name), file=sys.stderr)
    except NotFoundError:
        print("Repository {r} not found, creating it.."
              .format(r=repository_name))
        try:
            esclient.snapshot.create_repository(
                repository=repository_name,
                body=repository_config)
        except TransportError as e:
            print("Error when trying to create the snapshot repository '{r}':"
                  .format(r=repository_name), file=sys.stderr)
            print(e, file=sys.stderr)
            exit(1)


def create_snapshot(esclient, repository_name: str, snapshot_name: str):
    """Create a new snapshot, include the timestamp in the name."""
    snapshot_return = esclient.snapshot.create(
        repository=repository_name,
        snapshot=snapshot_name)
    if not ('accepted' in snapshot_return and snapshot_return['accepted']):
        raise Exception("Snapshot {n} could not be created."
                        .format(n=snapshot_name))

    print("Successfully created snapshot {s}".format(s=snapshot_name))
    return True


def get_snapshots(esclient, repository_name: str):
    """Get the list of all snapshots in the given repository."""
    # pylint: disable=unexpected-keyword-arg
    return esclient.cat.snapshots(repository=repository_name, format='json')


def delete_snapshots(esclient, repository_name: str, snapshots: list):
    """Deletes all snapshots in a list in the given repository."""
    delete_return = esclient.snapshot.delete(
        repository=repository_name,
        snapshot=snapshots)
    if not ('acknowledged' in delete_return and delete_return['acknowledged']):
        raise Exception("Delete of {s} failed.".format(s=snapshots))
    return True
