import time
from datetime import date, datetime, timedelta, tzinfo
from typing import Generator

import pytz

tz_pst: tzinfo = pytz.timezone('America/Los_Angeles')
tz_est: tzinfo = pytz.timezone('America/New_York')
tz_gmt8: tzinfo = pytz.timezone('Asia/Shanghai')
tz_utc: tzinfo = pytz.timezone('UTC')

# Local timezone
LOCAL_TZ: tzinfo = tz_gmt8


def now(tz: tzinfo | None = None) -> datetime:
    """Get the current time in the given timezone
    """
    if not tz:
        tz = LOCAL_TZ
    return datetime.now(tz)


def change_timezone(dt: datetime | date | str,
                    from_tz: str | tzinfo,
                    to_tz: str | tzinfo,
                    retain_tz_info: bool = True) -> datetime:
    """Convert given date/datetime from timezone A to timezone B

    E.g.:
    - Assuming `dt` is datetime "2024-11-21 00:00:00", with no timezone info
    - change_timezone(dt, tz_gmt8, tz_utc) -> datetime(2024, 11, 20, 16, 0, 0, tzinfo=<UTC>)
    """
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            dt = datetime.strptime(dt, '%Y-%m-%d')
    if isinstance(dt, date):
        dt = datetime.combine(dt, datetime.min.time())

    if isinstance(from_tz, str):
        from_tz = pytz.timezone(from_tz)
    if isinstance(to_tz, str):
        to_tz = pytz.timezone(to_tz)

    # If the datetime object is not timezone-aware, localize it with the source timezone
    if not dt.tzinfo:
        dt = from_tz.localize(dt)  # type: ignore
    res: datetime = dt.astimezone(to_tz)
    if not retain_tz_info:
        res = res.replace(tzinfo=None)
    return res


def dt_to_timestamp(dt: datetime | date | str,
                    source_tz: tzinfo,
                    target_tz: tzinfo | None = None) -> float:
    """Convert source tz's date/datetime object to timestamp of target tz
    - If target_tz is None, return the timestamp in the original timezone (source_tz), otherwise, convert the
      datetime object to the target timezone (target_tz)
    """
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            dt = datetime.strptime(dt, '%Y-%m-%d')
    if isinstance(dt, date):
        dt = datetime.combine(dt, datetime.min.time())

    # If the datetime object is not timezone-aware, localize it with the source timezone
    if not dt.tzinfo:
        dt = source_tz.localize(dt)  # type: ignore
    if not target_tz:
        return dt.timestamp()  # type: ignore
    return dt.astimezone(target_tz).timestamp()  # type: ignore


def timestamp_to_dt(timestamp: int,
                    source_tz: tzinfo,
                    target_tz: tzinfo | None = None,
                    retain_tz_info: bool = True) -> datetime:
    """Convert source tz's timestamp to datetime object of target tz
    - If target_tz is None, return the datetime object in the original timezone (source_tz), otherwise, convert the
      datetime object to the target timezone (target_tz)
    - If retain_tz_info=False, the timezone information will be removed on the returned datetime object, make it tz-unaware
    """
    if not target_tz:
        res: datetime = datetime.fromtimestamp(timestamp, source_tz)
    else:
        res: datetime = datetime.fromtimestamp(timestamp, source_tz).astimezone(target_tz)
    if not retain_tz_info:
        res = res.replace(tzinfo=None)
    return res


def round_down_to_minute(dt: datetime, backward: int | None = 0) -> datetime:
    """Round down the datetime to the latest minute
    - E.g.: (backward == 0) 2021-08-01 12:34:56.789 -> 2021-08-01 12:34:00.000
    - E.g.: (backward == 1) 2021-08-01 12:34:56.789 -> 2021-08-01 12:33:00.000
    - E.g.: (backward == 9) 2021-08-01 12:34:56.789 -> 2021-08-01 12:25:00.000
    - E.g.: (backward == 40) 2021-08-01 12:34:56.789 -> 2021-08-01 11:54:00.000
    """
    if not backward or backward <= 0:
        return dt - timedelta(seconds=dt.second, microseconds=dt.microsecond)
    if backward == 1:
        if dt.second > 0 or dt.microsecond > 0:
            dt -= timedelta(minutes=1)
        return dt.replace(second=0, microsecond=0)
    return round_down_to_minute(dt - timedelta(minutes=backward))


def round_down_to_hour(dt: datetime, backward: int | None = 0) -> datetime:
    """Round down the datetime to the latest hour
    - E.g.: (backward == 0) 2021-08-01 12:34:56.789 -> 2021-08-01 12:00:00.000
    - E.g.: (backward == 1) 2021-08-01 12:34:56.789 -> 2021-08-01 11:00:00.000
    - E.g.: (backward == 9) 2021-08-01 12:34:56.789 -> 2021-08-01 03:00:00.000
    - E.g.: (backward == 40) 2021-08-01 12:34:56.789 -> 2021-07-30 20:00:00.000
    """
    if not backward or backward <= 0:
        return dt - timedelta(minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    if backward == 1:
        if dt.minute > 0 or dt.second > 0 or dt.microsecond > 0:
            dt -= timedelta(hours=1)
        return dt.replace(minute=0, second=0, microsecond=0)
    return round_down_to_hour(dt - timedelta(hours=backward))


def round_down_to_day(dt: datetime, backward: int | None = 0) -> datetime:
    """Round down the datetime to the latest day
    - E.g.: (backward == 0) 2021-08-01 12:34:56.789 -> 2021-08-01 00:00:00.000
    - E.g.: (backward == 1) 2021-08-01 12:34:56.789 -> 2021-07-31 00:00:00.000
    - E.g.: (backward == 9) 2021-08-01 12:34:56.789 -> 2021-07-23 00:00:00.000
    - E.g.: (backward == 40) 2021-08-01 12:34:56.789 -> 2021-06-22 00:00:00.000
    """
    if not backward or backward <= 0:
        return dt - timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    if backward == 1:
        if dt.hour > 0 or dt.minute > 0 or dt.second > 0 or dt.microsecond > 0:
            dt -= timedelta(days=1)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return round_down_to_day(dt - timedelta(days=backward))


def date_gap(date1: str | date, date2: str | date) -> int:
    """Calculate the gap between two dates, e.g.:
    - date_gap('2021-08-01', '2021-08-02') -> 1
    - date_gap('2021-08-01', '2021-08-01') -> 0
    - date_gap('2021-08-01', '2021-07-31') -> -1
    """
    dt1: date = datetime.strptime(date1, '%Y-%m-%d').date() if isinstance(date1, str) else date1
    dt2: date = datetime.strptime(date2, '%Y-%m-%d').date() if isinstance(date2, str) else date2
    return (dt2 - dt1).days


def date_chunk(start_date: date, end_date: date, chunk_size: int) -> Generator[tuple[date, date], None, None]:
    """Loop in a date range in chunks, e.g.: from 2000-01-01 to 2000-01-10 in chunks of 3 days, and yield:
    - 2000-01-01 ~ 2000-01-03
    - 2000-01-04 ~ 2000-01-06
    - 2000-01-07 ~ 2000-01-09
    - 2000-01-10 ~ 2000-01-10
    """
    current_date: date = start_date
    while current_date <= end_date:
        chunk_end_date: date = min(current_date + timedelta(days=chunk_size - 1), end_date)
        yield current_date, chunk_end_date
        current_date = chunk_end_date + timedelta(days=1)


def compare_date(date1: str | date, date2: str | date) -> bool:
    """Compare two dates

    Returns:
        - True if date1 < date2 (date1 is earlier than date2)
        - False if date1 >= date2 (date1 is later than or equal to date2)
    """
    return date_gap(date1, date2) < 0


def shift_date(dt: str, year: int = 0, day: int = 0) -> str:
    """Shift the date by the given year and day

    E.g.:
    - shift_date('2021-08-01', 1, 0) -> '2022-08-01'
    - shift_date('2021-08-01', 0, 1) -> '2021-08-02'
    - shift_date('2021-08-01', 0, -1) -> '2021-07-31'
    """
    dt_obj: date = datetime.strptime(dt, '%Y-%m-%d').date()
    return (dt_obj + timedelta(days=day) + timedelta(days=365 * year)).strftime('%Y-%m-%d')


def next_run_time(interval_min: int, ahead_seconds: int = 5) -> datetime:
    """
    Calculate the next runtime based on the given time interval in minute

    根据time_interval，计算下次运行的时间，下一个整点时刻。
    目前只支持分钟和小时。
    :param time_interval: 运行的周期，15m，1h
    :param ahead_seconds: 预留的目标时间和当前时间的间隙
    :return: 下次运行的时间
    案例：
    15m  当前时间为：12:50:51  返回时间为：13:00:00
    15m  当前时间为：12:39:51  返回时间为：12:45:00
    10m  当前时间为：12:38:51  返回时间为：12:40:00
    5m  当前时间为：12:33:51  返回时间为：12:35:00
    5m  当前时间为：12:34:51  返回时间为：12:35:00

    1h  当前时间为：14:37:51  返回时间为：15:00:00
    2h  当前时间为：00:37:51  返回时间为：02:00:00

    30m  当前时间为：21日的23:33:51  返回时间为：22日的00:00:00
    5m  当前时间为：21日的23:57:51  返回时间为：22日的00:00:00

    ahead_seconds = 5
    15m  当前时间为：12:59:57  返回时间为：13:15:00，而不是 13:00:00
    """
    interval: timedelta = timedelta(minutes=interval_min)

    # Get current time, make it timezone aware of GMT+8
    now: datetime = datetime.now()
    target_time: datetime = now.replace(second=0, microsecond=0)

    # Increment the target time until it matches the interval and the buffer condition
    while True:
        target_time += timedelta(minutes=1)
        elapsed_since_midnight = target_time - target_time.replace(hour=0, minute=0, second=0, microsecond=0)

        if elapsed_since_midnight.seconds % interval.seconds == 0 and (target_time - now).seconds >= ahead_seconds:
            break

    return target_time


def sleep_until_run_time(interval_min: int, ahead_time: int = 1, if_sleep: bool = True):
    run_time = next_run_time(interval_min, ahead_time)

    if if_sleep:
        # Sleep until current time is VERY close to the run time
        time.sleep(max(0, (run_time - datetime.now()).seconds))

        # Break until the run time
        while True:
            if datetime.now() > run_time:
                break

    return run_time
