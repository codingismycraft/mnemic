"""Implements the function profiler."""

import datetime
import functools
import inspect
import uuid

def clear():
    """Removes all the profiling functions."""
    _ProfilingStatCollection.clear()

def profiler(foo):
    """Decorates a callable or coro making it profile-able.

    :param callable foo: The callable (sync or async) to profile.
    """
    _ProfilingStatCollection.register_profiling_function(foo)
    if inspect.iscoroutinefunction(foo):
        @functools.wraps(foo)
        async def _inner(*args, **kwargs):
            with _ProfilingStatCollection(foo):
                return await foo(*args, **kwargs)
    else:
        @functools.wraps(foo)
        def _inner(*args, **kwargs):
            with _ProfilingStatCollection(foo):
                return foo(*args, **kwargs)
    return _inner


def get_profiling_functions(use_async=False):
    """Returns all the available profiling functions.

    :param bool use_async: If true the returned functions will be async.

    :return: A list of sync/ async async functions one for each function to
        be profiled.  Used by trace client to wire the profile-able functions
        to tracing.

    :rtype: list
    """

    def make_func(profiling_callable_name, profile_func, tag):
        """Dynamically creates a profiling function.

        :param str profiling_callable_name:
        :param callable profile_func:
        :param str tag: The "tag" to use for the name of the returned function.

        :return: A profiled callable customized for the passed in parameters.
        :rtype: callable
        """

        if use_async:
            async def _inner():
                """The function that will be returned.

                :return: A profiling callable.
                :rtype: callable
                """
                return profile_func(profiling_callable_name)
        else:
            def _inner():
                """The function that will be returned.

                :return: A profiling callable.
                :rtype: callable
                """
                return profile_func(profiling_callable_name)

        _inner.__qualname__ = f'{profiling_callable_name}_{tag}'
        _inner.__name__ = f'{profiling_callable_name}_{tag}'

        return _inner

    func = []
    for name in _ProfilingStatCollection.get_profiling_callable_names():
        func.append(make_func(
            profiling_callable_name=name, profile_func=_get_hits, tag='hits')
        )
        func.append(make_func(
            profiling_callable_name=name, profile_func=_get_active_instances,
            tag='active_instances')
        )
        func.append(make_func(
            profiling_callable_name=name, profile_func=_get_average_time,
            tag='average_time')
        )
    return func


def _get_hits(callable_name):
    """Returns the number of hits for the passed-in callable name.

    :param str callable_name: The name of the callable.

    :returns: The number of hits for the passed-in callable name.
    :rtype: int
    """
    return _ProfilingStatCollection.get_stats_for_callable(callable_name).hits


def _get_active_instances(callable_name):
    """Returns the number of running_instances for the passed-in callable name.

    :param str callable_name: The name of the callable.

    :returns: The number of running_instances for the passed-in callable name.
    :rtype: int
    """
    return _ProfilingStatCollection.get_stats_for_callable(
        callable_name).running_instances


def _get_average_time(callable_name):
    """Returns the average_time in seconds for the passed-in callable name.

    :param str callable_name: The name of the callable.

    :returns: The average_time in seconds  for the passed-in callable name.
    :rtype: float
    """
    return _ProfilingStatCollection.get_stats_for_callable(
        callable_name).average_time


class _ProfilingStats:
    """Holds the profiling statistics for a callable.

    Instances of this class are kept in the ProfilingStatCollection as
    a class level dictionary making them available for querying at
    any time.

    :ivar int _hits: How many times a function was called.
    :ivar int _running_instances: How many instances of this functions are
        running (applicable to async calls ofc).
    :ivar float _average_time: The average duration for each call (in seconds).
    :ivar float _enter_time: The time the callable started  (in seconds).
    """

    _hits = 0
    _running_instances = 0
    _average_time = 0
    _enter_time = None

    def __init__(self):
        self._hits = 0
        self._running_instances = 0
        self._average_time = 0
        self._enter_time = {}
        self._completed = 0

    def enter(self, identifier):
        """Called when a callable starts."""
        self._hits += 1
        self._running_instances += 1
        self._enter_time[identifier] = datetime.datetime.now()

    def exit(self, identifier):
        """Called when a callable exits."""
        self._running_instances -= 1
        t_now = self._enter_time.pop(identifier)
        duration = (datetime.datetime.now() - t_now).total_seconds()
        x1 = self._average_time * self._completed + duration
        self._average_time = x1 / (self._completed + 1)
        self._completed += 1

    @property
    def hits(self):
        """Returns the number of hits.

        :return: The number of hits.
        :rtype: int
        """
        return self._hits

    @property
    def running_instances(self):
        """Returns the number of hits.

        :return: The number of concurrent instances.
        :rtype: int
        """
        return self._running_instances

    @property
    def average_time(self):
        """Returns the average duration in seconds.

        :return: The average duration in seconds.
        :rtype: float
        """
        return self._average_time

    def __repr__(self):
        return f'ProfilingStats: hits = {self._hits} ' \
               f'running_instances = {self._running_instances}' \
               f'avg. duration = {self._average_time}'


class _ProfilingStatCollection:
    """Profiling data accumulator.

    A context manager that has keeps a global state where it accumulates
    profiling statistics for callables.

    :cvar dict[str, ProfilingStats]: Maps callables to their profiling stats.

    :ivar str _func_name: The callable's name to profile.
    """

    _stats = {}

    @classmethod
    def clear(cls):
        """Removes all the registered profilers."""
        cls._stats = {}

    @classmethod
    def register_profiling_function(cls, func):
        cls._stats[func.__qualname__] = _ProfilingStats()

    def __init__(self, func):
        """Initializer.

        :param callable func: The callable to profile.
        """
        self._func_name = func.__qualname__
        self._uuid = None

    def __enter__(self):
        """Called when the callable starts."""
        self._uuid = uuid.uuid4()
        self._stats[self._func_name].enter(self._uuid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when the callable exits."""
        self._stats[self._func_name].exit(self._uuid)

    @classmethod
    def get_profiling_callable_names(cls):
        """Returns a list with the names of all callables that are profiled.

        :returns: A list with the names of all callables that are profiled.
        :rtype: list[str]
        """
        return list(cls._stats.keys())

    @classmethod
    def get_stats_for_callable(cls, callable_name):
        """Returns the number of hits for the passed-in callable name.
    
        :param str callable_name: The name of the callable.
        :rtype: _ProfilingStats
        """
        return cls._stats.get(callable_name)
