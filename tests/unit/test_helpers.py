from essnapshot.helpers import retention_timedelta, open_configfile
from essnapshot.helpers import snapshot_name, check_snapshots_in_progress
from essnapshot.helpers import find_delete_eligible_snapshots
from datetime import datetime, timezone, timedelta
import pytest
import re


@pytest.fixture
def es_snapshot_list_progress():
    return [
        {
            "id": "essnapshot_2020-08-05_11-24-34",
            "status": "SUCCESS",
            "start_epoch": "1596626674",
            "start_time": "11:24:34",
            "end_epoch": "1596626674",
            "end_time": "11:24:34",
            "duration": "0s",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        },
        {
            "id": "essnapshot_2020-08-05_11-24-48",
            "status": "IN_PROGRESS",
            "start_epoch": "1596626688",
            "start_time": "11:24:48",
            "end_epoch": "0",
            "end_time": "00:00:00",
            "duration": "62ms",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        }
    ]


@pytest.fixture
def es_snapshot_list():
    return [
        {
            "id": "essnapshot_2020-08-05_11-24-34",
            "status": "SUCCESS",
            "start_epoch": "1596626674",
            "start_time": "11:24:34",
            "end_epoch": "1596626674",
            "end_time": "11:24:34",
            "duration": "0s",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        },
        {
            "id": "essnapshot_2020-08-05_11-24-48",
            "status": "SUCCESS",
            "start_epoch": "1596626688",
            "start_time": "11:24:48",
            "end_epoch": "1596626688",
            "end_time": "11:24:48",
            "duration": "0s",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        },
        {
            "id": "essnapshot_2020-08-05_11-32-57",
            "status": "SUCCESS",
            "start_epoch": "1596627177",
            "start_time": "11:32:57",
            "end_epoch": "1596627177",
            "end_time": "11:32:57",
            "duration": "201ms",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        },
        {
            "id": "essnapshot_2020-08-05_11-40-40",
            "status": "SUCCESS",
            "start_epoch": "1596627639",
            "start_time": "11:40:39",
            "end_epoch": "1596627639",
            "end_time": "11:40:39",
            "duration": "0s",
            "indices": "0",
            "successful_shards": "0",
            "failed_shards": "0",
            "total_shards": "0"
        }
    ]


@pytest.mark.parametrize("convert_time, expected_result", [
    ("60", timedelta(seconds=60)),
    ("1s", timedelta(seconds=1)),
    ("1m", timedelta(minutes=1)),
    ("1h", timedelta(hours=1)),
    ("1d", timedelta(days=1))
])
def test_retention_timedelta(convert_time, expected_result):
    assert retention_timedelta(convert_time) == expected_result


def test_retention_timedelta_exception_invalid_time_string():
    with pytest.raises(ValueError):
        assert retention_timedelta('1-D')


def test_retention_timedelta_exception_unkown_unit():
    with pytest.raises(ValueError):
        assert retention_timedelta('1Z')


def test_retention_timedelta_exception_if_integer_is_given():
    with pytest.raises(TypeError):
        assert retention_timedelta(1)


def test_open_configfile_success():
    assert isinstance(open_configfile('tests/configs/success.yaml'), dict)


def test_open_configfile_not_found():
    with pytest.raises(SystemExit) as e:
        open_configfile('tests/configs/missing.yaml')
    assert e.type == SystemExit
    assert e.value.code == 2


def test_open_configfile_no_valid_yaml():
    with pytest.raises(SystemExit) as e:
        open_configfile('tests/configs/no.yaml')
    assert e.type == SystemExit
    assert e.value.code == 3


def test_open_configfile_missing_required_param():
    with pytest.raises(ValueError):
        assert open_configfile('tests/configs/missing_param.yaml')


def test_snapshot_name():
    pattern = re.compile(r"essnapshot_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    assert pattern.match(snapshot_name())


def test_check_snapshots_in_progress_true(es_snapshot_list_progress):
    assert check_snapshots_in_progress(es_snapshot_list_progress)


def test_check_snapshots_in_progress_false(es_snapshot_list):
    assert not check_snapshots_in_progress(es_snapshot_list)


def test_find_delete_eligible_snapshots(es_snapshot_list):
    des = find_delete_eligible_snapshots(
        es_snapshot_list,
        '1h',
        datetime(2020, 8, 5, 12, 25, 00, tzinfo=timezone.utc))
    assert des == [
        'essnapshot_2020-08-05_11-24-34',
        'essnapshot_2020-08-05_11-24-48'
    ]
