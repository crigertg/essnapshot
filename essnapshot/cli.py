"""This script is for running the esssnapshot utility interactivly."""
from optparse import OptionParser
from time import sleep
from essnapshot.helpers import open_configfile, snapshot_name
from essnapshot.helpers import check_snapshots_in_progress
from essnapshot.helpers import find_delete_eligible_snapshots
import essnapshot.es as es


def wait_for_running_snapshots(esclient, repository_name):
    """Run in a loop until all running snapshots are done or failed.

    Parameters
    ----------
    esclient : Elasticsearch
        the client for the elasticsearch cluster to connect to.
    repostiory_name : str
        the name of the repository to check for running snapshots

    Returns
    -------
    nothing
    """
    while check_snapshots_in_progress(
        es.get_snapshots(esclient, repository_name)
    ):
        print("Waiting until running snapshots are done..")
        sleep(1)


def main():
    """Runs the essnapshot tool."""
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile",
                      help="Path to configuration file. "
                      "See example and documentation at "
                      "https://github.com/gricertg/essnapshot",
                      metavar="FILE")
    options = parser.parse_args()[0]

    if options.configfile is None:
        parser.error('No configuration file given.')

    config = open_configfile(options.configfile)

    # if the optional es_connections parameter is given, use it
    # otherwise we set None to use the default config
    esconfig = config['es_connections'] if 'es_connections' in config else None
    esclient = es.initialize_es_client(esconfig)

    es.connection_check(esclient)
    es.ensure_snapshot_repo(
        esclient,
        config['repository_name'],
        config['repository'])
    wait_for_running_snapshots(esclient, config['repository_name'])
    es.create_snapshot(esclient, config['repository_name'], snapshot_name())

    wait_for_running_snapshots
    delete_eligible_snapshots = find_delete_eligible_snapshots(
        es.get_snapshots(esclient, config['repository_name']),
        config['retention_time'])

    if len(delete_eligible_snapshots) > 0:
        es.delete_snapshots(esclient, config['repository_name'],
                            delete_eligible_snapshots)


if __name__ == "__main__":
    main()
