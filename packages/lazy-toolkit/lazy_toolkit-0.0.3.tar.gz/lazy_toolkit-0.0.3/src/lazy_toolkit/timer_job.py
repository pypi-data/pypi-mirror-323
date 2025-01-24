import random
import threading
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from logging import Logger
from typing import Callable

from .enum import Frequency
from .exception import exception_msg
from .time import now, tz_utc


class TimerJobBase:
    """Defines a timer job that should be executed at a serious of specific time of the day, or by a fixed interval
    """

    def __init__(self,
                 job_name: str,
                 interval: int,
                 timers: list[str] | None,
                 task: Callable,
                 logger: Logger | None,
                 *task_args,
                 **task_kwargs):
        """
        Args:
            interval (int): Interval between job's each execution, in seconds
            timers (list[str]): A list of 24H formatted string time (HH:MM:SS, UTC), e.g. ['11:45:14', '19:19:81']
                - Note: if timers is provided, the interval will be ignored
                - All timers are in UTC timezone
            task (Callable): The function to be executed
            task_args (tuple): Positional arguments to be passed to the task
            task_kwargs (dict): Keyword arguments to be passed to the task
        """
        self.logger: Logger | None = logger
        self.job_name: str = job_name

        # Task and params
        self._task: Callable = task
        self._task_args: tuple = task_args
        self._task_kwargs: dict = task_kwargs

        # TimerJob configuration
        self.timers: list[str] = timers if timers else list()
        self.timer_index: int = 0

        # The interval value of the next execution from current time
        self.interval_to_next_execution: float = float(interval)
        if self.interval_to_next_execution < 0 and not self.timers:
            raise ValueError('Invalid TimerJob configuration, interval or utc_timestamps must be provided')

        # Flag to indicate if this job is timed or interval based
        self.timed: bool = bool(self.timers)

    def __str__(self):
        if self.timed:
            return f'[TimedJob-{self.job_name}]'
        return f'[IntervalJob-{self.job_name}]'

    def __repr__(self):
        return self.__str__()

    def _get_next_execution_str(self, move_index: bool = False) -> tuple[str, bool]:
        """Get the next execution time of this job if it's configured to be executed at specific times of the day

        Args:
            move_index (bool, optional): Move the index to the next execution time. Defaults to False.
                - This can only happen when current execution time is invalid (e.g. in the past)

        Returns:
            tuple[str, bool]: The next execution time in 24H formatted string (HH:MM:SS, UTC), and a flag indicating if it's the next day
        """
        if self.timer_index < len(self.timers):
            # Get next execution time of the day
            execution_time_str: str = self.timers[self.timer_index]
            next_day: bool = False
            if move_index:
                self.timer_index += 1
        else:
            # Execution list is exhausted, restart from beginning
            execution_time_str: str = self.timers[0]
            next_day: bool = True
            if move_index:
                self.timer_index = 1
        return execution_time_str, next_day

    def refresh_execution_interval(self, scheduler_waited: float = 0.001) -> float:
        """Get the next execution interval of this job based on provided config

        Args:
            scheduler_waited (float): The time that scheduler already waited for this round of execution

        Returns:
            float: The next execution interval in seconds
        """
        raise NotImplementedError()

    def execute(self):
        """Execute the task of this job
        """
        try:
            self._task(*self._task_args, **self._task_kwargs)
        except Exception as e:
            if self.logger:
                self.logger.error(f'{self} Uncaught exception from task: {exception_msg(e)}')
            raise e


"""
Interval Job
"""


class IntervalJobConfig:
    """Configuration for IntervalJob
    """

    def __init__(self, interval: Frequency | int, repeat_on: str | None = None, avoid_congestion: bool = False, ):
        """
        Args:
            interval (Frequency): Interval of job's each execution, it can only be 1 minute, 1 hour or 1 day
            avoid_congestion (bool, optional): Avoid job congestion by add a random value to first invocation. Defaults to False, and cannot be used with `repeat_on`
                - For example, without this option, 10 jobs with same interval will be always executed at the same time, this will cause congestion in some cases
                - With this option, the first invocation will be delayed by a random value to avoid job congestion
            repeat_on (str, optional): Repeat the job on specific timestamp in format of 'HH:MM:SS' based on interval
                - If `repeat_on` is True, then `interval` value can only be 1 minute, 1 hour or 1 day
                - E.g.1: `repeat_on=11:45:14` with `interval=60` will repeat the job at ??:??:14 every minute
                - E.g.2: `repeat_on=11:45:14` with `interval=3600` will repeat the job at ??:45:14 every hour
                - E.g.3: `repeat_on=11:45:14` with `interval=86400` will repeat the job at 11:45:14 every day
                - This is different from TimedJob as a TimedJob will not have "repeat" or "interval" behavior but only on specific timestamp
        """
        self.interval_s: int = interval.to_minutes() * 60 if isinstance(interval, Frequency) else interval
        self.repeat_on: str | None = repeat_on
        self.avoid_congestion: bool = avoid_congestion

        if self.repeat_on and interval != Frequency._1m and interval != Frequency._1h and interval != Frequency._1d:
            raise ValueError(
                'Invalid IntervalJob configuration: "repeat_on" can only be used with a fixed job interval of 1m, 1h or 1d')

        if self.repeat_on:
            try:
                datetime.strptime(self.repeat_on, '%H:%M:%S')
            except Exception:
                raise ValueError('Invalid IntervalJob configuration: "repeat_on" must be in format of "HH:MM:SS"')
            self.avoid_congestion = False


class IntervalJob(TimerJobBase):
    """Defines a timer job that should be executed at a fixed interval
    """

    def __init__(self,
                 job_name: str,
                 config: IntervalJobConfig,
                 task: Callable,
                 *task_args,
                 **task_kwargs):
        """
        Args:
            job_name (str): The name of this job
            config (IntervalJobConfig): Configuration for this interval job
            task (Callable): The function to be executed
            task_args (tuple): Positional arguments to be passed to the task
            task_kwargs (dict): Keyword arguments to be passed to the task
        """
        interval: int = config.interval_s
        avoid_congestion: bool = config.avoid_congestion
        super().__init__(job_name, interval, None, task, *task_args, **task_kwargs)

        self.original_interval: float = interval
        self.prev_execution_time: datetime | None = None
        self.repeat_on: str | None = config.repeat_on

        # Repeat timestamp is only valid for interval of 60, 3600 or 86400
        # - Compare the current time (not UTC) with the repeat timestamp to get the next execution time and adjust `interval_to_next_execution`
        # - If interval is daily, then respect all of the H/M/S of provided `repeat_on`
        # - If interval is hourly, then respect only M/S of provided `repeat_on`
        # - If interval is minutely, then only S will be respected
        if self.repeat_on:
            now: datetime = datetime.now()
            repeat_time: datetime = datetime.strptime(self.repeat_on, '%H:%M:%S')
            repeat_datetime: datetime = datetime(
                now.year,
                now.month,
                now.day,
                repeat_time.hour if interval == 86400 else now.hour,
                repeat_time.minute if interval == 3600 or interval == 86400 else now.minute,
                repeat_time.second)

            # Calculate the time difference between now and the next repeat timestamp
            # If `to_next_repeat` is negative, then adjust `repeat_datetime` to next
            # minute/hour/day according to interval until it's positive
            to_next_repeat: int = int((repeat_datetime - now).total_seconds())
            while to_next_repeat < 0:
                if interval == 60:
                    repeat_datetime += timedelta(minutes=1)
                elif interval == 3600:
                    repeat_datetime += timedelta(hours=1)
                elif interval == 86400:
                    repeat_datetime += timedelta(days=1)
                to_next_repeat = int((repeat_datetime - now).total_seconds())

            # Set the interval to the next repeat timestamp
            self.interval_to_next_execution = to_next_repeat

        # Random delay in seconds to avoid job congestion if option is enabled
        # - Add to `interval_to_next_execution` directly for the first invocation
        elif avoid_congestion:
            random_delay: float = 0
            if interval < 5:
                random_delay = random.uniform(0, 5)
            elif interval < 30:
                random_delay = random.uniform(0, interval)
            else:
                random_delay = random.uniform(0, 30)

            # Adjust the initial value with random delay to the next execution time
            self.interval_to_next_execution += random_delay

    def refresh_execution_interval(self, scheduler_waited: float = 0.001) -> float:
        # Calculate the execution interval on current round of execution
        self.interval_to_next_execution -= scheduler_waited
        return self.interval_to_next_execution

    def execute(self):
        _now: datetime = now(tz_utc)

        # If a job is called with `execute()` then `interval_to_next_execution` here is guaranteed to be <= 0
        # - From job's second round of execution, adjust interval drift
        if self.prev_execution_time:
            execution_gap: float = (_now - self.prev_execution_time).total_seconds()
            self.prev_execution_time = _now

            # Drift multiplier is hardcoded, and it is a magic number
            # - Due to the time cost of calling `super().execute()`, the actual drift will always be larger than the
            #   calculated drift, so a multiplier is used to adjust the calculated drift to try to keep the calculated
            #   drift as close to the actual drift as possible
            # - It needs to be adjusted based on the actual execution time of the job
            # - Currently tried 2 is too large and 1.5 is too small, so try 1.7 for now
            drift_multiplier: float = 1.7

            # If drift is positive, then current interval is longer than original, reduce next interval with drift
            # If drift is negative, then current interval is shorter than original, reset next interval to original
            drift: float = execution_gap - self.original_interval
            if drift > 0:
                self.interval_to_next_execution = self.original_interval - drift * drift_multiplier + self.interval_to_next_execution
            else:
                self.interval_to_next_execution = self.original_interval
        else:
            self.prev_execution_time = _now
            self.interval_to_next_execution = self.original_interval

        super().execute()


class IntervalJobScheduler(threading.Thread):
    """Executor thread for TimerJob - Fixed interval job
    """

    def __init__(self, logger: Logger | None, max_parallel_tasks: int = 3, daemon: bool = False):
        super().__init__(daemon=daemon)

        self.logger: Logger | None = logger
        self.__thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.__cancellation: threading.Event = threading.Event()
        self.jobs: list[IntervalJob] = list()

    def __get_nearest_job(self, scheduler_waited: float = 0.001) -> tuple[list[IntervalJob], float]:
        """Return the nearest timer job based on their next execution time from current time
        - This ensures the next job to be executed is always the one with the shortest interval starting from now

        Args:
            scheduler_waited (float): The time that scheduler already waited for this round of execution
        """
        # Minus all jobs' interval by the time that scheduler already waited then sort
        self.jobs.sort(key=lambda job: job.refresh_execution_interval(scheduler_waited))

        # Get all jobs that are ready to be executed on current time (interval_to_next_execution <= 0) and calculate
        # the next waiting time for scheduler to wait
        res: list[IntervalJob] = list()
        scheduler_should_wait: float = 0
        for job in self.jobs:
            # If remaining interval to next execution is 0 or negative, means the job is ready to be executed
            if job.interval_to_next_execution <= 0:
                res.append(job)
            else:
                # The first job with positive interval is the time that scheduler should wait in next round
                scheduler_should_wait = job.interval_to_next_execution
                break

        return res, scheduler_should_wait

    def add_job(self, job: IntervalJob):
        self.jobs.append(job)

    def stop(self):
        if self.logger:
            self.logger.warning('IntervalJobScheduler stopping...')
        self.__cancellation.set()

    def is_stopped(self) -> bool:
        return self.__cancellation.is_set()

    def run(self):
        if not self.jobs:
            if self.logger:
                self.logger.warning('No interval job to schedule, IntervalJobScheduler quit')
            return

        # Scheduler's initial waiting interval is the minimum interval value of all registered jobs
        min_interval: float = min([job.original_interval for job in self.jobs])
        scheduler_wait: float = min_interval

        if self.logger:
            self.logger.info(
                f'IntervalJobScheduler started, total jobs: {len(self.jobs)}, initially wait for next schedule phase in {scheduler_wait}s')
        try:
            while True:
                self.__cancellation.wait(scheduler_wait)
                if not self.__cancellation.is_set():
                    # Get a list of jobs that are ready to be executed on current time
                    jobs, scheduler_wait = self.__get_nearest_job(scheduler_wait)
                    if len(jobs) == len(self.jobs):
                        # If all jobs are ready to be executed, then scheduler should wait for the minimum interval
                        scheduler_wait = min_interval
                    else:
                        scheduler_wait = min(scheduler_wait, min_interval)

                    if not jobs:
                        if self.logger:
                            self.logger.debug(
                                f'No interval job on schedule, wait for next schedule phase in {scheduler_wait}s')
                        continue

                    for job in jobs:
                        if self.logger:
                            self.logger.info(
                                f'{job} scheduled on: {datetime.now(timezone.utc)}')
                        if not self.__cancellation.is_set():
                            self.__thread_pool.submit(job.execute)
                        else:
                            break
                    if self.logger:
                        self.logger.info(
                            f'Scheduling done, scheduler will wait for next schedule phase in {scheduler_wait}s')
                else:
                    if self.logger:
                        self.logger.warning('IntervalJobScheduler\'s execution has been cancelled')
                    break
        except Exception as e:
            if self.logger:
                self.logger.error(f'IntervalJobScheduler stopped running: {exception_msg(e)}')


"""
Timed Job
"""


class TimedJob(TimerJobBase):
    """Defines a timed job that should be executed at a serious of specific time of the day, or by a fixed interval
    """

    def __init__(self,
                 job_name: str,
                 task: Callable,
                 timers: list[str] | None,
                 *args,
                 **kwargs):
        """
        Args:
            job_name (str): The name of this job
            task (Callable): The function to be executed
            timers (list[str]): A list of 24H formatted string time (HH:MM:SS, UTC), e.g. ['11:45:14', '19:19:81']
                - Note: if timers is provided, the interval will be ignored
                - All timers are in UTC timezone
        """
        super().__init__(job_name, -1, timers, task, *args, **kwargs)

    def refresh_execution_interval(self) -> float:
        now: datetime = datetime.now(timezone.utc)

        # For timed job, calculate the interval to the next execution time of the day
        # - Using loop in case of the next execution time is in the past (as provided timestamps is not in order)
        to_next_execution: float = -1
        execution_date: datetime = deepcopy(now)
        move_index: bool = False
        while True:
            execution_time_str, next_day = self._get_next_execution_str(move_index)
            if next_day:
                execution_date += timedelta(days=1)

            if len(execution_time_str) == 5:
                execution_time_str = f'{execution_time_str}:00'
            execution_time = datetime.time(datetime.strptime(execution_time_str, '%H:%M:%S'))
            execution_datetime: datetime = datetime(
                execution_date.year,
                execution_date.month,
                execution_date.day,
                execution_time.hour,
                execution_time.minute,
                execution_time.second,
                tzinfo=timezone.utc)

            to_next_execution = (execution_datetime - now).total_seconds()
            if to_next_execution >= 0:
                break
            else:
                move_index = True

        self.interval_to_next_execution = int(to_next_execution)
        return self.interval_to_next_execution


class TimedJobScheduler(threading.Thread):
    """Executor thread for TimerJob - Timed type
    """

    def __init__(self, logger: Logger | None, max_parallel_tasks: int = 3, daemon: bool = False):
        super().__init__(daemon=daemon)

        self.logger: Logger | None = logger
        self.__thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.__cancellation: threading.Event = threading.Event()
        self.jobs: list[TimedJob] = list()

    def __adjust_timed_job_index(self, job: TimedJob):
        """Forward the index of the timed job to the next execution time
        - Why do this in job executor? Simply for thread safety
        """
        if job.timed:
            if job.timer_index < len(job.timers):
                job.timer_index += 1
            else:
                job.timer_index = 0

    def __get_nearest_job(self) -> list[TimedJob]:
        """Return the nearest timer job based on their next execution time from current time
        - This ensures the next job to be executed is always the one with the shortest interval starting from now

        Returns:
            list[TimerJob]: The list of timer jobs who are with same interval to the next execution time
        """
        self.jobs.sort(key=lambda job: job.refresh_execution_interval())

        res: list[TimedJob] = [self.jobs[0]]
        for job in self.jobs[1:]:
            if job.interval_to_next_execution == res[0].interval_to_next_execution:
                res.append(job)
            else:
                break
        return res

    def add_job(self, job: TimedJob):
        self.jobs.append(job)

    def stop(self):
        if self.logger:
            self.logger.warning('TimedJobScheduler stopping...')
        self.__cancellation.set()

    def is_stopped(self) -> bool:
        return self.__cancellation.is_set()

    def run(self):
        if not self.jobs:
            if self.logger:
                self.logger.warning('No timed job to schedule, TimedJobScheduler quit')
            return

        if self.logger:
            self.logger.info(f'TimedJobScheduler started, total jobs: {len(self.jobs)}')
        try:
            while True:
                jobs: list[TimedJob] = self.__get_nearest_job()

                # Wait for current job's execution interval
                if self.logger:
                    self.logger.debug(
                        f'Scheduling next timed job batch in {jobs[0].interval_to_next_execution}s, total jobs: {len(jobs)}, expected execution time: {datetime.now(timezone.utc) + timedelta(seconds=jobs[0].interval_to_next_execution)}')
                self.__cancellation.wait(jobs[0].interval_to_next_execution)
                if not self.__cancellation.is_set():
                    for job in jobs:
                        if self.logger:
                            self.logger.info(f'{job} scheduled on: {datetime.now(timezone.utc)}')
                        self.__adjust_timed_job_index(job)
                        self.__thread_pool.submit(job.execute)
                else:
                    if self.logger:
                        self.logger.warning('TimedJobScheduler execution has been cancelled')
                    break
        except Exception as e:
            if self.logger:
                self.logger.error(f'TimedJobScheduler stopped running: {exception_msg(e)}')


class TimerJobExecutor:
    """Executor for TimerJob
    """

    def __init__(self, logger: Logger | None, max_parallel_tasks: int = 5):
        self.logger: Logger | None = logger
        self.max_parallel_tasks: int = max_parallel_tasks
        self.__interval_scheduler: IntervalJobScheduler = IntervalJobScheduler(logger, max_parallel_tasks)
        self.__timed_scheduler: TimedJobScheduler = TimedJobScheduler(logger, max_parallel_tasks)

    def add_job(self, job: TimerJobBase):
        if self.logger:
            self.logger.info(f'Adding job: {job}')
        if isinstance(job, TimedJob):
            self.__timed_scheduler.add_job(job)
        elif isinstance(job, IntervalJob):
            self.__interval_scheduler.add_job(job)

    def run(self):
        if self.logger:
            self.logger.info('TimerJob executor starting...')

        self.__interval_scheduler.start()
        self.__timed_scheduler.start()
        self.__interval_scheduler.join()
        self.__timed_scheduler.join()

    def stop(self):
        try:
            self.__interval_scheduler.stop()
            self.__timed_scheduler.stop()
        except Exception as e:
            if self.logger:
                self.logger.error(f'TimerJob executor failed to stop: {exception_msg(e)}')

    def is_stopped(self) -> bool:
        return self.__interval_scheduler.is_stopped() and self.__timed_scheduler.is_stopped()

    def reset(self):
        self.__interval_scheduler = IntervalJobScheduler(self.logger, self.max_parallel_tasks)
        self.__timed_scheduler = TimedJobScheduler(self.logger, self.max_parallel_tasks)
        if self.logger:
            self.logger.info('TimerJob executor has been reset')
