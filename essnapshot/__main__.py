from optparse import OptionParser
from time import sleep
from essnapshot.helpers import open_configfile, snapshot_name
from essnapshot.helpers import check_snapshots_in_progress
from essnapshot.helpers import find_delete_eligible_snapshots
import es

# parse the only needed command line parameter
parser = OptionParser()
parser.add_option("-c", "--config", dest="configfile",
                  help="Path to configuration file",
                  metavar="FILE")
(options, args) = parser.parse_args()

# check if configfile parameter is given
if options.configfile is None:
    parser.error('No configuration file given.')

# fetch config from configfile
config = open_configfile(options.configfile)


def wait_for_running_snapshots():
    while check_snapshots_in_progress(
        es.get_snapshots(esclient, config['repository_name'])
    ):
        print("Waiting until running snapshots are done..")
        sleep(1)


esclient = es.initialize_es_client()
es.connection_check(esclient)
es.ensure_snapshot_repo(
    esclient,
    config['repository_name'],
    config['repository'])
wait_for_running_snapshots()
snapshot_name = snapshot_name()
es.create_snapshot(esclient, config['repository_name'], snapshot_name)


# find all snapshots to delete
wait_for_running_snapshots
delete_eligible_snapshots = find_delete_eligible_snapshots(
    es.get_snapshots(esclient, config['repository_name']),
    config['retention_time'])

# delete snapshots older than the configured retention time
if len(delete_eligible_snapshots) > 0:
    es.delete_snapshots(esclient, config['repository_name'],
                        delete_eligible_snapshots)
