#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: ISC

from abc import ABC, abstractmethod

from . import _patcher as patcher
from ._checkpoints import checkpoint, green_checkpoint
from ._libraries import current_async_library, current_green_library


class Event(ABC):
    __slots__ = ()

    @abstractmethod
    def __bool__(self, /):
        return self.is_set()

    @abstractmethod
    def set(self, /):
        raise NotImplementedError

    @abstractmethod
    def cancel(self, /):
        raise NotImplementedError

    @abstractmethod
    def is_set(self, /):
        raise NotImplementedError

    @abstractmethod
    def is_cancelled(self, /):
        raise NotImplementedError


class DummyEvent(Event):
    __slots__ = ()

    def __new__(cls, /):
        if cls is DummyEvent:
            self = DUMMY_EVENT
        else:
            self = super().__new__(cls)

        return self

    def __init_subclass__(cls, /, **kwargs):
        msg = "type 'DummyEvent' is not an acceptable base type"
        raise TypeError(msg)

    def __reduce__(self, /):
        return "DUMMY_EVENT"

    def __repr__(self, /):
        return "DUMMY_EVENT"

    def __bool__(self, /):
        return True

    def __await__(self, /):
        yield from checkpoint().__await__()

        return True

    def wait(self, /, timeout=None):
        green_checkpoint()

        return True

    def set(self, /):
        return False

    def cancel(self, /):
        return False

    def is_set(self, /):
        return True

    def is_cancelled(self, /):
        return False


DUMMY_EVENT = object.__new__(DummyEvent)


class BaseEvent(Event):
    __slots__ = (
        "_is_cancelled",
        "_is_unset",
    )

    def __new__(cls, /):
        self = super().__new__(cls)

        self._is_unset = [True]
        self._is_cancelled = False

        return self

    def __bool__(self, /):
        return not self._is_unset

    def cancel(self, /):
        cancelled = self._is_cancelled

        if not cancelled and (is_unset := self._is_unset):
            try:
                is_unset.pop()
            except IndexError:
                pass
            else:
                self._is_cancelled = cancelled = True

        return cancelled

    def is_set(self, /):
        return not self._is_unset

    def is_cancelled(self, /):
        return self._is_cancelled


class GreenEvent(BaseEvent):
    __slots__ = ()

    def __new__(cls, /):
        if cls is GreenEvent:
            library = current_green_library()

            if library == "threading":
                self = ThreadingEvent.__new__(ThreadingEvent)
            elif library == "eventlet":
                self = EventletEvent.__new__(EventletEvent)
            elif library == "gevent":
                self = GeventEvent.__new__(GeventEvent)
            else:
                msg = f"unsupported green library {library!r}"
                raise RuntimeError(msg)
        else:
            self = super().__new__(cls)

        return self

    @abstractmethod
    def wait(self, /, timeout=None):
        raise NotImplementedError


@patcher.once
def get_threading_event_class():
    global ThreadingEvent

    from ._thread import allocate_lock

    class ThreadingEvent(GreenEvent):
        __slots__ = ("__lock",)

        def __new__(cls, /):
            self = super().__new__(cls)

            self.__lock = allocate_lock()
            self.__lock.acquire()

            return self

        def __init_subclass__(cls, /, **kwargs):
            msg = "type 'ThreadingEvent' is not an acceptable base type"
            raise TypeError(msg)

        def __reduce__(self, /):
            msg = f"cannot reduce {self!r}"
            raise TypeError(msg)

        def wait(self, /, timeout=None):
            success = True

            if self._is_unset:
                if timeout is None:
                    success = self.__lock.acquire()
                elif timeout > 0:
                    success = self.__lock.acquire(timeout=timeout)
                else:
                    success = self.__lock.acquire(blocking=False)
            else:
                green_checkpoint()

            return success

        def set(self, /):
            success = True

            if is_unset := self._is_unset:
                try:
                    is_unset.pop()
                except IndexError:
                    success = False
                else:
                    self.__lock.release()
            else:
                success = False

            return success

    return ThreadingEvent


@patcher.once
def get_eventlet_event_class():
    global EventletEvent

    from eventlet.hubs import get_hub as get_eventlet_hub
    from greenlet import getcurrent as current_greenlet

    try:
        from eventlet.hubs import _threadlocal as eventlet_hubs
    except ImportError:
        current_eventlet_hub = get_eventlet_hub
    else:

        def current_eventlet_hub():
            try:
                hub = eventlet_hubs.hub
            except AttributeError:
                hub = None

            return hub

    patcher.patch_eventlet()

    class EventletEvent(GreenEvent):
        __slots__ = (
            "__greenlet",
            "__hub",
        )

        def __new__(cls, /):
            self = super().__new__(cls)

            self.__hub = get_eventlet_hub()
            self.__greenlet = None

            return self

        def __init_subclass__(cls, /, **kwargs):
            msg = "type 'EventletEvent' is not an acceptable base type"
            raise TypeError(msg)

        def __reduce__(self, /):
            msg = f"cannot reduce {self!r}"
            raise TypeError(msg)

        def wait(self, /, timeout=None):
            success = True

            if self._is_unset:
                self.__greenlet = current_greenlet()

                try:
                    hub = self.__hub

                    if timeout is None:
                        timer = None
                    elif timeout > 0:
                        timer = hub.schedule_call_local(
                            timeout,
                            self.__set,
                            False,
                        )
                    else:
                        timer = hub.schedule_call_local(
                            0,
                            self.__set,
                            False,
                        )

                    try:
                        success = hub.switch()
                    finally:
                        if timer is not None:
                            timer.cancel()
                except BaseException:
                    self.cancel()
                    raise
                finally:
                    self.__greenlet = None
            else:
                green_checkpoint()

            return success

        def __set(self, /, success):
            if (greenlet := self.__greenlet) is not None:
                greenlet.switch(success)

        def set(self, /):
            success = True

            if is_unset := self._is_unset:
                try:
                    is_unset.pop()
                except IndexError:
                    success = False
                else:
                    hub = current_eventlet_hub()

                    if hub is self.__hub:
                        hub.schedule_call_global(
                            0,
                            self.__set,
                            True,
                        )
                    else:
                        self.__hub.schedule_call_threadsafe(
                            0,
                            self.__set,
                            True,
                        )
            else:
                success = False

            return success

    return EventletEvent


@patcher.once
def get_gevent_event_class():
    global GeventEvent

    from gevent import get_hub as get_gevent_hub
    from gevent.event import Event as GeventPEvent

    try:
        from gevent._hub_local import get_hub_if_exists as current_gevent_hub
    except ImportError:
        current_gevent_hub = get_gevent_hub

    class GeventEvent(GreenEvent):
        __slots__ = (
            "__event",
            "__hub",
        )

        def __new__(cls, /):
            self = super().__new__(cls)

            self.__hub = get_gevent_hub()
            self.__event = None

            return self

        def __init_subclass__(cls, /, **kwargs):
            msg = "type 'GeventEvent' is not an acceptable base type"
            raise TypeError(msg)

        def __reduce__(self, /):
            msg = f"cannot reduce {self!r}"
            raise TypeError(msg)

        def wait(self, /, timeout=None):
            success = True

            if self._is_unset:
                self.__event = GeventPEvent()

                try:
                    hub = self.__hub

                    if not hasattr(hub, "_aiologic_watcher_count"):
                        hub._aiologic_watcher_count = 0
                        hub._aiologic_watcher = hub.loop.async_()

                        # suppress LoopExit
                        hub._aiologic_watcher.start(lambda: None)

                    hub._aiologic_watcher_count += 1

                    try:
                        if timeout is None:
                            success = self.__event.wait()
                        elif timeout > 0:
                            success = self.__event.wait(timeout)
                        else:
                            success = self.__event.wait(0)
                    finally:
                        hub._aiologic_watcher_count -= 1

                        if not hub._aiologic_watcher_count:
                            hub._aiologic_watcher.close()

                            del hub._aiologic_watcher
                            del hub._aiologic_watcher_count
                except BaseException:
                    self.cancel()
                    raise
                finally:
                    self.__event = None
            else:
                green_checkpoint()

            return success

        def __set(self, /):
            if (event := self.__event) is not None:
                event.set()

        def set(self, /):
            success = True

            if is_unset := self._is_unset:
                try:
                    is_unset.pop()
                except IndexError:
                    success = False
                else:
                    hub = current_gevent_hub()

                    if hub is self.__hub:
                        self.__set()
                    else:
                        if (loop := self.__hub.loop) is not None:
                            try:
                                loop.run_callback_threadsafe(self.__set)
                            except ValueError:  # event loop is destroyed
                                pass
            else:
                success = False

            return success

    return GeventEvent


class ThreadingEvent(GreenEvent):  # noqa: F811
    __slots__ = ()

    def __new__(cls, /):
        try:
            cls = get_threading_event_class()  # noqa: PLW0642
        except ImportError:
            raise NotImplementedError from None
        else:
            self = cls.__new__(cls)

        return self


class EventletEvent(GreenEvent):  # noqa: F811
    __slots__ = ()

    def __new__(cls, /):
        try:
            cls = get_eventlet_event_class()  # noqa: PLW0642
        except ImportError:
            raise NotImplementedError from None
        else:
            self = cls.__new__(cls)

        return self


class GeventEvent(GreenEvent):  # noqa: F811
    __slots__ = ()

    def __new__(cls, /):
        try:
            cls = get_gevent_event_class()  # noqa: PLW0642
        except ImportError:
            raise NotImplementedError from None
        else:
            self = cls.__new__(cls)

        return self


class AsyncEvent(BaseEvent):
    __slots__ = ()

    def __new__(cls, /):
        if cls is AsyncEvent:
            library = current_async_library()

            if library == "asyncio":
                self = AsyncioEvent.__new__(AsyncioEvent)
            elif library == "trio":
                self = TrioEvent.__new__(TrioEvent)
            else:
                msg = f"unsupported async library {library!r}"
                raise RuntimeError(msg)
        else:
            self = super().__new__(cls)

        return self

    @abstractmethod
    def __await__(self, /):
        raise NotImplementedError


@patcher.once
def get_asyncio_event_class():
    global AsyncioEvent

    from asyncio import get_running_loop as get_running_asyncio_loop
    from asyncio.exceptions import InvalidStateError

    class AsyncioEvent(AsyncEvent):
        __slots__ = (
            "__future",
            "__loop",
        )

        def __new__(cls, /):
            self = super().__new__(cls)

            self.__loop = get_running_asyncio_loop()
            self.__future = None

            return self

        def __init_subclass__(cls, /, **kwargs):
            msg = "type 'AsyncioEvent' is not an acceptable base type"
            raise TypeError(msg)

        def __reduce__(self, /):
            msg = f"cannot reduce {self!r}"
            raise TypeError(msg)

        def __await__(self, /):
            if self._is_unset:
                self.__future = self.__loop.create_future()

                try:
                    yield from self.__future.__await__()
                except BaseException:
                    self.cancel()
                    raise
                finally:
                    self.__future = None
            else:
                yield from checkpoint().__await__()

            return True

        def __set(self, /):
            if (future := self.__future) is not None:
                try:
                    future.set_result(True)
                except InvalidStateError:  # future is cancelled
                    pass

        def set(self, /):
            success = True

            if is_unset := self._is_unset:
                try:
                    is_unset.pop()
                except IndexError:
                    success = False
                else:
                    try:
                        loop = get_running_asyncio_loop()
                    except RuntimeError:  # no running event loop
                        loop = None

                    if loop is self.__loop:
                        self.__set()
                    else:
                        try:
                            self.__loop.call_soon_threadsafe(self.__set)
                        except RuntimeError:  # event loop is closed
                            pass
            else:
                success = False

            return success

    return AsyncioEvent


@patcher.once
def get_trio_event_class():
    global TrioEvent

    from trio import RunFinishedError
    from trio.lowlevel import (
        Abort,
        current_task as current_trio_task,
        current_trio_token,
        reschedule as reschedule_trio_task,
        wait_task_rescheduled as wait_trio_task_rescheduled,
    )

    class TrioEvent(AsyncEvent):
        __slots__ = (
            "__task",
            "__token",
        )

        def __new__(cls, /):
            self = super().__new__(cls)

            self.__token = current_trio_token()
            self.__task = None

            return self

        def __init_subclass__(cls, /, **kwargs):
            msg = "type 'TrioEvent' is not an acceptable base type"
            raise TypeError(msg)

        def __reduce__(self, /):
            msg = f"cannot reduce {self!r}"
            raise TypeError(msg)

        def __await__(self, /):
            if self._is_unset:
                self.__task = current_trio_task()

                yield from wait_trio_task_rescheduled(self.__abort).__await__()

                self.__task = None
            else:
                yield from checkpoint().__await__()

            return True

        def __abort(self, /, raise_cancel):
            self.__task = None

            self.cancel()

            return Abort.SUCCEEDED

        def __set(self, /):
            if (task := self.__task) is not None:
                reschedule_trio_task(task)

        def set(self, /):
            success = True

            if is_unset := self._is_unset:
                try:
                    is_unset.pop()
                except IndexError:
                    success = False
                else:
                    try:
                        token = current_trio_token()
                    except RuntimeError:  # no called trio.run
                        token = None

                    if token is self.__token:
                        self.__set()
                    else:
                        try:
                            self.__token.run_sync_soon(self.__set)
                        except RunFinishedError:
                            pass
            else:
                success = False

            return success

    return TrioEvent


class AsyncioEvent(AsyncEvent):  # noqa: F811
    __slots__ = ()

    def __new__(cls, /):
        try:
            cls = get_asyncio_event_class()  # noqa: PLW0642
        except ImportError:
            raise NotImplementedError from None
        else:
            self = cls.__new__(cls)

        return self


class TrioEvent(AsyncEvent):  # noqa: F811
    __slots__ = ()

    def __new__(cls, /):
        try:
            cls = get_trio_event_class()  # noqa: PLW0642
        except ImportError:
            raise NotImplementedError from None
        else:
            self = cls.__new__(cls)

        return self
