"""This module contains helper functions for the essnapshot utility."""
import sys
import re
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta


def retention_timedelta(time: str) -> timedelta:
    """returns the given retention time from String as timedelta object

    Parameters
    ----------
    time : str
        A String in the Format <digit>*<S|M|H|D, for e.g. 30D for 30 days

    Returns
    -------
    timedelta
        a timedelta object generated from the time string is returned
    """
    pattern = re.compile(r"^(?P<value>\d+)(?P<unit>[a-zA-Z])?$")
    match = pattern.match(time)
    if not match:
        raise ValueError("Unable to parse given time String {t}."
                         .format(t=time))
    if match.group('unit'):
        unit = match.group('unit').upper()
    else:
        unit = 'S'
    time_value = int(match.group('value'))
    timedelta_args = {
        'S': {'seconds': time_value},
        'M': {'minutes': time_value},
        'H': {'hours': time_value},
        'D': {'days': time_value},
    }
    if unit in timedelta_args:
        return timedelta(**timedelta_args[unit])
    else:
        raise ValueError("Unsupported time unit {u}".format(u=unit))


def open_configfile(filepath: str) -> dict:
    """returns yaml config from file if file exists and is valid yaml

    After the configfile is opened and parsed a check if required parameters
    are present.

    Parameters
    ----------
    filepath : str
        A string which is a valid absolute or relational path to the configfile

    Returns
    -------
    dict
        The parsed YAML config file is returned in as a dict
    """
    try:
        Path(filepath).resolve(strict=True)
    except FileNotFoundError as e:
        print("Unable to access configfile {f}:"
              .format(f=filepath), file=sys.stderr)
        print(e, file=sys.stderr)
        exit(2)

    with open(filepath) as configfile:
        try:
            config = yaml.load(configfile, Loader=yaml.FullLoader)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
            print("Unable to parse {f} as YAML:"
                  .format(f=filepath), file=sys.stderr)
            print(e, file=sys.stderr)
            exit(3)

        required_config_keys = [
            'repository_name',
            'repository',
            'retention_time'
        ]
        for key in required_config_keys:
            if key not in config:
                raise ValueError("Could not find required paramter {k} in {f}."
                                 .format(k=key, f=filepath))
        return config


def snapshot_name() -> str:
    """returns a name for the snapshot with a date postfix

    Parameters
    ----------
    no parameters

    Returns
    -------
    str
        The name will look like this: essnapshot_2020-05-12_23-54-01
    """

    snapshot_timestamp = datetime.utcnow()
    timestamp_string = snapshot_timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_name = "essnapshot_{d}".format(d=timestamp_string)
    return snapshot_name


def check_snapshots_in_progress(snapshots: list):
    """Checks if there are snapshots in the IN_PROGRESS state

    Parameters
    ----------
    snapshots : list
        a list of snapshots returned from ES must be provided

    Returns
    -------
    bool
        returns true if any snapshots are IN_PROGRESS, otherwise false
    """
    if len([s['id'] for s in snapshots if s['status'] == 'IN_PROGRESS']) > 0:
        return True
    else:
        return False


def find_delete_eligible_snapshots(
        snapshots: list,
        retention_time: str,
        from_time: datetime = datetime.now(timezone.utc)) -> list:
    """Find snapshots older than the given retention time

    Parameters
    ----------
    snapshots : list
        a list of snapshots returned from ES must be provided
    retention_time : str
        the time string which will be parsed by retention_timedelta
    from_time : datetime
        the point in time from which to start the calculaton (should be now)

    Returns
    -------
    list
        a list of all delete eligible snapshot names will be returned
    """
    delete_eligible_snapshots = []
    for snapshot in snapshots:
        snapshot_timestamp = datetime.fromtimestamp(int(snapshot['end_epoch']),
                                                    tz=timezone.utc)
        snapshot_age = from_time - snapshot_timestamp
        if snapshot_age > retention_timedelta(retention_time):
            delete_eligible_snapshots.append(snapshot['id'])
            print("Marked snapshot {s} as eligible for deletion."
                  .format(s=snapshot['id']))
    return delete_eligible_snapshots
