import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from logging import Logger
from threading import Event
from typing import Callable

from .mixin import ContainableEnum

EXPIRATION_DURATION = 86400


class TaskState(ContainableEnum):
    InProgress = 'in_progress'
    Finished = 'finished'
    Faulted = 'faulted'
    Cancelled = 'cancelled'


def report_progress(progress_reporter: Callable[[int, int, str | None], None] | None,
                    current_progress: int,
                    current_phase: int = 1,
                    phase_name: str = ''):
    """Report the progress of current task
    """
    if not progress_reporter:
        return
    if current_progress is None or current_progress < 0 or current_progress > 100:
        return
    try:
        progress_reporter(current_progress, current_phase, phase_name)
    except BaseException:
        pass


class TaskInfo:
    """Define an executed task
    """

    def __init__(self, id: str):
        self.future: Future | None = None
        self.cancel_event: Event | None = None
        self.id: str = id
        self.state: TaskState = TaskState.InProgress
        self.phase_count: int = 1  # The number of phases in the task
        self.phase_name: str = ''
        self.current_phase: int = 1
        self.progress: int = 0  # The progress of the task on current phase, if task with 1 phase only then it represents the overall progress of the task
        self.error: str = ''
        self.submitted_on: datetime = datetime.now()
        self.completed_on: datetime = datetime(1970, 1, 1)
        self.duration: int = -1

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'state': str(self.state),
            'phase_count': self.phase_count,
            'phase_name': self.phase_name,
            'current_phase': self.current_phase,
            'progress': self.progress,
            'error': self.error,
            'submitted_on': self.submitted_on,
            'completed_on': self.completed_on,
            'duration': self.duration,
        }


class TaskRunner:
    def __init__(self,
                 logger: Logger | None,
                 max_parallel_tasks: int = 5,
                 expiration_duration: int = EXPIRATION_DURATION):
        self.logger: Logger | None = logger
        # TODO: persist task status to disk
        self.tasks: dict[str, TaskInfo] = dict()
        self.max_parallel_tasks: int = max_parallel_tasks
        self.expiration_duration: int = expiration_duration
        self.__thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_parallel_tasks)

    def __mark_task_completed(self, task_id: str, termination_state: TaskState, error: str = ''):
        """Mark a task as completed with given state
        """
        if termination_state == TaskState.Faulted:
            if self.logger:
                self.logger.error(f'Task {task_id} faulted, error: {error}')
        if termination_state == TaskState.Cancelled:
            if self.logger:
                self.logger.info(f'Task {task_id} cancelled')
        if termination_state == TaskState.Finished:
            if self.logger:
                self.tasks[task_id].progress = 100
                self.logger.info(f'Task {task_id} finished')

        now: datetime = datetime.now()
        self.tasks[task_id].state = termination_state
        self.tasks[task_id].completed_on = now
        self.tasks[task_id].error = error
        self.tasks[task_id].duration = int((now - self.tasks[task_id].submitted_on).total_seconds())

    def __run_task_with_catch(self,
                              task_id: str,
                              task_func: Callable,
                              progress_reporter: Callable | None,
                              cancel_event: Event | None,
                              args: tuple,
                              kwargs: dict):
        """Run given task
        """
        try:
            if self.logger:
                self.logger.info(f'Executing task: {task_id}, task function: {task_func.__name__}')
            task_func(*args, **kwargs,
                      progress_reporter=progress_reporter,
                      cancel_event=cancel_event)
            self.__mark_task_completed(task_id, TaskState.Finished)
        except Exception as e:
            self.__mark_task_completed(task_id, TaskState.Faulted, str(e))

    def __get_active_task_count(self) -> int:
        """Get active task count also cleanup expired tasks
        """
        expired: list[str] = list()
        res: int = 0
        for id in self.tasks:
            if self.tasks[id].state == TaskState.InProgress:
                res += 1
            else:
                completed_on: datetime | None = self.tasks[id].completed_on
                if completed_on:
                    if (datetime.now() - completed_on).total_seconds() > self.expiration_duration:
                        expired.append(id)
                else:
                    expired.append(id)

        if expired:
            if self.logger:
                self.logger.info(f'Found {len(expired)} expired tasks, cleaning up')
            for id in expired:
                self.tasks.pop(id)
        return res

    def submit_task(self,
                    task_func: Callable,
                    callback_lambda: Callable | None,
                    support_reporter: bool,
                    support_cancel: bool,
                    phase_count: int,
                    *task_args,
                    **task_kwargs) -> str | None:
        """Submit a function as a concurrent task and executing in the background

        Args:
            task_func (Callable): The target function to be executed
            callback_lambda (Callable | None): The optional callback function to be executed after the task is finished
            support_reporter (bool): If the task supports reporting execution progress
                To support this, target function must have a keyword argument named `progress_reporter`
            support_cancel (bool): If the task supports cancellation
                To support this, target function must have a keyword argument named `cancel_event`
            phase_count (int): The number of phases in the task, used with progress reporter
            task_args (tuple): The positional arguments to be passed to the target function
            task_kwargs (dict): The keyword arguments to be passed to the target function
        """
        if self.__get_active_task_count() >= self.max_parallel_tasks:
            if self.logger:
                self.logger.warning(
                    f'Failed to submit new task, maximum parallel tasks reached: {self.max_parallel_tasks}')
            return None
        if not task_func:
            return None

        task: TaskInfo = TaskInfo(str(uuid.uuid4()))
        task.phase_count = phase_count if phase_count >= 1 else 1
        if support_cancel:
            task.cancel_event = Event()

        if self.logger:
            self.logger.info(f'Submitting new task: {task.id}, task function: {task_func.__name__}')
        if support_reporter:
            # The reporter function is used to report the progress of current task object via closure
            def progress_reporter(progress: int,
                                  current_phase: int = 1,
                                  phase_name: str = ''):
                t: TaskInfo = self.tasks[task.id]
                t.progress = progress
                t.current_phase = current_phase
                t.phase_name = phase_name
                t.duration = int((datetime.now() - t.submitted_on).total_seconds())
            future: Future = self.__thread_pool.submit(
                self.__run_task_with_catch, task.id, task_func, progress_reporter, task.cancel_event, task_args, task_kwargs)
        else:
            future: Future = self.__thread_pool.submit(
                self.__run_task_with_catch, task.id, task_func, None, task.cancel_event, task_args, task_kwargs)
        task.future = future
        self.tasks[task.id] = task

        if callback_lambda:
            future.add_done_callback(callback_lambda)
        return task.id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel an executing task
        1. Try to stop the future if the task is not started
        2. On failure, check if task supports cancellation

        If task not found, return True
        """
        if self.logger:
            self.logger.info(f'Canceling task: {task_id}')
        if task_id in self.tasks:
            future = self.tasks[task_id].future
            if not future:
                if self.logger:
                    self.logger.warning(f'Failed to cancel task: {task_id}, future not found')
                return False

            if not future.done():
                cancelled: bool = future.cancel()
                if not cancelled and self.tasks[task_id].cancel_event:
                    self.tasks[task_id].cancel_event.set()  # type: ignore
                    cancelled = True
                if cancelled:
                    self.__mark_task_completed(task_id, TaskState.Cancelled)
                    return True

                if self.logger:
                    self.logger.warning(f'Failed to cancel task: {task_id}')
                return False
        return True

    def get_task_state(self, task_id: str) -> TaskInfo | None:
        """Check the running state of given task IDs
        """
        return self.tasks.get(task_id, None)

    def is_task_done(self, task_id: str) -> bool:
        """Check if a task is done, this includes all termination states like cancel, failure, etc.
        - If task not found, return True
        """
        if task_id in self.tasks:
            return self.tasks[task_id].state != TaskState.InProgress
        return True

    def is_task_successful(self, task_id: str) -> bool:
        """Check if a task is done and successful
        - If task not found, return True
        """
        if task_id in self.tasks:
            return self.tasks[task_id].state == TaskState.Finished and not self.tasks[task_id].error
        return True
