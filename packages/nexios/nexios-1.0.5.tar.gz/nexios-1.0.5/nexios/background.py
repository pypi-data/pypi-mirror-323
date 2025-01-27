
from __future__ import annotations
from nexios.utils.cuncurrency import run_in_threadpool
import sys
import typing

if sys.version_info >= (3, 10):  
    from typing import ParamSpec
else: 
    from typing_extensions import ParamSpec



P = ParamSpec("P")
T = typing.TypeVar("T")
AwaitableCallable = typing.Callable[..., typing.Awaitable[T]]

@typing.overload
def is_async_callable(obj: AwaitableCallable[T]): ...
class BackgroundTask:
    def __init__(self, func: typing.Callable[P, typing.Any], *args: P.args, **kwargs: P.kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = is_async_callable(func)

    async def __call__(self) -> None:
        if self.is_async:
            await self.func(*self.args, **self.kwargs)
        else:
            await run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks(BackgroundTask):
    def __init__(self, tasks: typing.Sequence[BackgroundTask] | None = None):
        self.tasks = list(tasks) if tasks else []

    def add_task(self, func: typing.Callable[P, typing.Any], *args: P.args, **kwargs: P.kwargs) -> None:
        task = BackgroundTask(func, *args, **kwargs)
        self.tasks.append(task)

    async def __call__(self) -> None:
        for task in self.tasks:
            await task()
