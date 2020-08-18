"""This module contains functions for ES communication used by essnapshot."""
import sys
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch import TransportError, ConnectionError


def initialize_es_client(es_connections: list) -> Elasticsearch:
    """initialize an instance of the ES client and return it.

    Parameters
    ----------
    es_connections : list
        the parameter is optional. It should contain hosts definitions
        as decribed in
        https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch

    Returns
    -------
    Elasticsearch
        An Elasticsearch instance client is returned for further usage
    """
    return Elasticsearch(es_connections)


def connection_check(esclient: Elasticsearch) -> bool:
    """Make sure that the connection to the ES cluster is working

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the ES cluster which should be checked must be given

    Returns
    -------
    bool
        The function will return True if the ES cluster is online
    """
    if not esclient.ping():
        print("Can't connect to ES Cluster.", file=sys.stderr)
        try:
            esclient.cluster.health()
        except ConnectionError as e:
            print(e, file=sys.stderr)
            exit(1)
    return True


def ensure_snapshot_repo(
        esclient: Elasticsearch,
        repository_name: str,
        repository_config: dict):
    """Check if snapshot repo exists, if not, create it.

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the ES cluster to connect to
    repository_name : str
        the name of the repository to ensure
    repository_config : dict
        the configuration of the ES snapshot, described as body under
        https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.client.SnapshotClient.create

    Returns
    -------
    nothing
    """
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


def create_snapshot(
        esclient: Elasticsearch,
        repository_name: str,
        snapshot_name: str) -> bool:
    """Creates a new snapshot Elasticsearch snapshot

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the ES cluster to connect to
    repository_name : str
        the name of the snapshot repository to use
    snapshot_name : str
        The name of the Elasticsearch snapshot

    Returns
    -------
    bool
        returns True if the creation of the snapshot was successful
    """
    snapshot_return = esclient.snapshot.create(
        repository=repository_name,
        snapshot=snapshot_name)
    if not ('accepted' in snapshot_return and snapshot_return['accepted']):
        raise Exception("Snapshot {n} could not be created."
                        .format(n=snapshot_name))

    print("Successfully created snapshot {s}".format(s=snapshot_name))
    return True


def get_snapshots(esclient, repository_name: str) -> list:
    """Get all snapshots in the given repository and return them as list.

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the ES cluster to connect to
    repository_name : str
        the name of the snapshot repository to use

    Returns
    -------
    list
        a list of multiple dictionaries (one per snapshot) is returned, see
        https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.client.CatClient.snapshots
    """
    # pylint: disable=unexpected-keyword-arg
    return esclient.cat.snapshots(repository=repository_name, format='json')


def delete_snapshots(esclient, repository_name: str, snapshots: list) -> bool:
    """Deletes all snapshots in a list in the given repository

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the ES cluster to connect to
    repository_name : str
        the name of the snapshot repository to use
    snapshots : list
        a list of snapshot names to delete

    Returns
    -------
    bool
        returns True if the delete operation was successful
    """
    delete_return = esclient.snapshot.delete(
        repository=repository_name,
        snapshot=snapshots)
    if not ('acknowledged' in delete_return and delete_return['acknowledged']):
        raise Exception("Delete of {s} failed.".format(s=snapshots))
    return True
