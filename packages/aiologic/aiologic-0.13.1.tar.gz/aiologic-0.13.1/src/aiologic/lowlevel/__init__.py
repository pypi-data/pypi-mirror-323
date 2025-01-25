#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: ISC

from ._checkpoints import (
    async_checkpoint as async_checkpoint,
    asyncio_checkpoints_cvar as asyncio_checkpoints_cvar,
    cancel_shielded_checkpoint as cancel_shielded_checkpoint,
    checkpoint as checkpoint,
    checkpoint_if_cancelled as checkpoint_if_cancelled,
    curio_checkpoints_cvar as curio_checkpoints_cvar,
    eventlet_checkpoints_cvar as eventlet_checkpoints_cvar,
    gevent_checkpoints_cvar as gevent_checkpoints_cvar,
    green_checkpoint as green_checkpoint,
    repeat_if_cancelled as repeat_if_cancelled,
    threading_checkpoints_cvar as threading_checkpoints_cvar,
    trio_checkpoints_cvar as trio_checkpoints_cvar,
)
from ._events import (
    DUMMY_EVENT as DUMMY_EVENT,
    AsyncEvent as AsyncEvent,
    DummyEvent as DummyEvent,
    Event as Event,
    GreenEvent as GreenEvent,
)
from ._flags import (
    Flag as Flag,
)
from ._ident import (
    current_async_task as current_async_task,
    current_async_task_ident as current_async_task_ident,
    current_async_token as current_async_token,
    current_async_token_ident as current_async_token_ident,
    current_green_task as current_green_task,
    current_green_task_ident as current_green_task_ident,
    current_green_token as current_green_token,
    current_green_token_ident as current_green_token_ident,
    current_thread as current_thread,
    current_thread_ident as current_thread_ident,
)
from ._libraries import (
    AsyncLibraryNotFoundError as AsyncLibraryNotFoundError,
    GreenLibraryNotFoundError as GreenLibraryNotFoundError,
    asyncio_running as asyncio_running,
    curio_running as curio_running,
    current_async_library as current_async_library,
    current_async_library_cvar as current_async_library_cvar,
    current_async_library_tlocal as current_async_library_tlocal,
    current_green_library as current_green_library,
    current_green_library_tlocal as current_green_library_tlocal,
    eventlet_running as eventlet_running,
    gevent_running as gevent_running,
    threading_running as threading_running,
    trio_running as trio_running,
)
from ._markers import (
    MISSING as MISSING,
    MissingType as MissingType,
)
from ._patcher import (
    patch_eventlet as patch_eventlet,
    patch_threading as patch_threading,
)
from ._sockets import (
    socketpair as socketpair,
)
from ._threads import (
    ThreadLocal as ThreadLocal,
    add_thread_finalizer as add_thread_finalizer,
    remove_thread_finalizer as remove_thread_finalizer,
    start_new_thread as start_new_thread,
)

# add old aiologic.lowlevel submodules for backward compatibility with 0.12.0
__modules = __import__("sys").modules
__modules[f"{__name__}.checkpoints"] = __modules[f"{__name__}._checkpoints"]
__modules[f"{__name__}.events"] = __modules[f"{__name__}._events"]
__modules[f"{__name__}.flags"] = __modules[f"{__name__}._flags"]
__modules[f"{__name__}.ident"] = __modules[f"{__name__}._ident"]
__modules[f"{__name__}.libraries"] = __modules[f"{__name__}._libraries"]
__modules[f"{__name__}.markers"] = __modules[f"{__name__}._markers"]
__modules[f"{__name__}.patcher"] = __modules[f"{__name__}._patcher"]
__modules[f"{__name__}.socket"] = __modules[f"{__name__}._socket"]
__modules[f"{__name__}.sockets"] = __modules[f"{__name__}._sockets"]
__modules[f"{__name__}.thread"] = __modules[f"{__name__}._thread"]
__modules[f"{__name__}.threads"] = __modules[f"{__name__}._threads"]

del __modules

# modify __module__ for shorter repr() and better pickle support
for __value in list(globals().values()):
    if getattr(__value, "__module__", "").startswith(f"{__name__}."):
        try:
            __value.__module__ = __name__
        except AttributeError:
            pass

    del __value
