..
  SPDX-FileCopyrightText: 2024 Ilya Egorov <0x42005e1f@gmail.com>
  SPDX-License-Identifier: CC-BY-4.0

========
aiologic
========

**aiologic** is an async-aware library for tasks synchronization and their
communication in different threads and different event loops. For example, if
there is interaction between classic synchronous (threaded) code and
asynchronous one, between two asynchronous codes in different threads, or any
other combination that you want. Let's take a look at the example:

.. code:: python

    from threading import Thread

    import anyio

    from aiologic import Lock

    lock = Lock()


    async def func(i, j):
        print(f"thread={i} task={j} started")

        async with lock:
            await anyio.sleep(1)

        print(f"thread={i} task={j} stopped")


    async def main(i):
        async with anyio.create_task_group() as tasks:
            for j in range(2):
                tasks.start_soon(func, i, j)


    for i in range(2):
        Thread(target=anyio.run, args=[main, i]).start()

It prints something like this:

.. code-block::

    thread=0 task=0 started
    thread=1 task=0 started
    thread=0 task=1 started
    thread=1 task=1 started
    thread=0 task=0 stopped
    thread=1 task=0 stopped
    thread=0 task=1 stopped
    thread=1 task=1 stopped

As you can see, when using ``aiologic.Lock``, tasks from different event loops
are all able to acquire a lock. In the same case if you use ``anyio.Lock``, it
will raise a ``RuntimeError``. And ``threading.Lock`` will cause a deadlock.

Why?
====

Cooperative (coroutines, greenlets) and preemptive (threads) multitasking are
not usually used together. Typically, you have an application that uses only
threads (classic application) or only coroutines/greenlets (asynchronous
application). But sometimes so different styles need to coexist.

.. code:: python

    # cooperative multitasking (deterministic execution order)

    async def foo():
        print("foo (in)")
        await anyio.sleep(0)  # switch to bar()
        print("foo (out)")

    async def bar():
        print("bar (in)")
        await anyio.sleep(0)  # switch to foo()
        print("bar (out)")

    async with anyio.create_task_group() as tasks:
        tasks.start_soon(foo)
        tasks.start_soon(bar)

.. code:: python

    # preemptive multitasking (non-deterministic execution order)

    def foo():
        print("foo (in)")
        time.sleep(0)  # maybe switch to the main thread
        time.sleep(0)  # maybe switch to bar()
        print("foo (out)")

    def bar():
        print("bar (in)")
        time.sleep(0)  # maybe switch to the main thread
        time.sleep(0)  # maybe switch to foo()
        print("bar (out)")

    with ThreadPoolExecutor(2) as executor:
        executor.submit(foo)
        executor.submit(bar)

The main problem is notification when some event occurs, since both
synchronization and communication depend on it. Cooperative-only (async-only)
and preemptive-only (sync-only) worlds already have suitable primitives, but
when they collide, things get much more complicated. Here are some of those
situations (assuming that the primary multitasking style is cooperative):

* Using a library that manages threads itself
  (e.g. a web app).
* Reusing the same worker thread for different asynchronous operations
  (e.g. to access a serial port).
* Requirement to guarantee even distribution of CPU resources between different
  groups of tasks
  (e.g. a chatbot working in multiple chats).
* Interaction of two or more frameworks that cannot be run in the same event
  loop
  (e.g. a GUI framework with any other framework).
* Parallelization of code whose synchronous part cannot be easily delegated to
  a thread pool
  (e.g. a CPU-bound network application that needs low response times).
* Simultaneous use of incompatible concurrency libraries in different threads
  (e.g. due to legacy code).
* `Accelerating asynchronous applications in a nogil world
  <https://discuss.python.org/t/asyncio-in-a-nogil-world/30694>`_.

These situations have one thing in common: you may need a way to interact
between threads, at least one of which may run an event loop. However, you
cannot use primitives from the threading module because they block the event
loop. You also cannot use primitives from the asyncio module because they
`are not thread-safe/thread-aware <https://stackoverflow.com/a/79198672>`_.

Known solutions (only for some special cases) use one of the following ideas:

- Delegate waiting to a thread pool (executor), e.g. via ``run_in_executor()``.
- Delegate calling to an event loop, e.g. via
  ``call_soon_threadsafe()``.
- Perform polling via timeouts and non-blocking calls.

All these ideas have disadvantages. Polling consumes a lot of CPU resources,
actually blocks the event loop for a short time, and has poor responsiveness.
The ``call_soon_threadsafe()`` approach does not actually do any real work
until the event loop scheduler handles a callback. The ``run_in_executor()``
approach requires a worker thread per call and has issues with cancellation and
timeouts:

.. code:: python

    import asyncio
    import threading

    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(8)
    semaphore = threading.Semaphore(0)


    async def main():
        loop = asyncio.get_running_loop()

        for _ in range(8):
            try:
                await asyncio.wait_for(loop.run_in_executor(
                    executor,
                    semaphore.acquire,
                ), 0)
            except asyncio.TimeoutError:
                pass


    print('active threads:', threading.active_count())  # 1

    asyncio.run(main())

    print('active threads:', threading.active_count())  # 9 - wow, thread leak!

    # program will hang until you press Control-C

However, *aiologic* has none of these disadvantages. Using its approach based
on low-level events, it gives you much more than you can get with alternatives.
That's why it's there, and that's why you're here.

Features
========

* Python 3.8+ support
* `CPython <https://www.python.org/>`_ and `PyPy <https://pypy.org/>`_ support
* Pickling and weakrefing support
* Cancellation and timeouts support
* Optional `Trio-style checkpoints
  <https://trio.readthedocs.io/en/stable/reference-core.html#checkpoints>`_:

  * enabled by default for Trio itself
  * disabled by default for all others

* Only one checkpoint per asynchronous call:

  * exactly one context switch if checkpoints are enabled
  * zero or one context switch if checkpoints are disabled

* Fairness wherever possible (with some caveats)
* Thread safety wherever possible
* Zero required dependencies
* Lock-free implementation
* Bundled stub files

Synchronization primitives:

* Semaphores: counting and bounded
* Locks: primitive, ownable and reentrant
* Capacity limiters: simple and reentrant
* Condition variables
* Barriers: single-use and cyclic
* Events: one-time, reusable and countdown
* Resource guards

Communication primitives:

* Queues: FIFO, LIFO and priority

Supported concurrency libraries:

* `asyncio <https://docs.python.org/3/library/asyncio.html>`_
  and `trio <https://trio.readthedocs.io>`_ (coroutine-based)
* `eventlet <https://eventlet.readthedocs.io>`_
  and `gevent <https://www.gevent.org/>`_ (greenlet-based)

All synchronization and communication primitives are implemented entirely on
effectively atomic operations, which gives `an incredible speedup on PyPy
<https://gist.github.com/x42005e1f/149d3994d5f7bd878def71d5404e6ea4>`_ compared
to alternatives from the threading module. All this works because of GIL, but
per-object locks also ensure that `the same operations are still atomic
<https://peps.python.org/pep-0703/#container-thread-safety>`_, so aiologic also
works when running in a `free-threaded mode
<https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython>`_.

Installation
============

Install from `PyPI <https://pypi.org/project/aiologic/>`_ (recommended):

.. code:: console

    pip install aiologic

Or from `GitHub <https://github.com/x42005e1f/aiologic>`_:

.. code:: console

    pip install git+https://github.com/x42005e1f/aiologic.git

You can also use other package managers, such as
`uv <https://github.com/astral-sh/uv>`_.

Derivatives
===========

* `x42005e1f/culsans <https://github.com/x42005e1f/culsans>`_ - Janus-like
  sync-async queue. Unlike ``aiologic`` queues, provides API compatible
  interfaces.

Communication channels
======================

GitHub Discussions: https://github.com/x42005e1f/aiologic/discussions

Feel free to post your questions and ideas here.

Support
=======

If you like ``aiologic`` and want to support its development, star `its
repository on GitHub <https://github.com/x42005e1f/aiologic>`_.

.. image:: https://starchart.cc/x42005e1f/aiologic.svg?variant=adaptive
  :target: https://starchart.cc/x42005e1f/aiologic

License
=======

The ``aiologic`` library is `REUSE <https://reuse.software/>`_-compliant and is
offered under multiple licenses:

* All original source code is licensed under `ISC <LICENSES/ISC.txt>`_.
* All original test code is licensed under `0BSD <LICENSES/0BSD.txt>`_.
* All documentation is licensed under `CC-BY-4.0 <LICENSES/CC-BY-4.0.txt>`_.
* All configuration is licensed under `CC0-1.0 <LICENSES/CC0-1.0.txt>`_.

For more accurate information, check the individual files.
