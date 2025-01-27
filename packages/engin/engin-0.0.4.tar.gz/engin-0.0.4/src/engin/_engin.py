import asyncio
import logging
import os
import signal
from asyncio import Event, Task
from collections.abc import Iterable
from contextlib import AsyncExitStack
from itertools import chain
from types import FrameType
from typing import ClassVar, TypeAlias

from engin import Entrypoint
from engin._assembler import AssembledDependency, Assembler
from engin._block import Block
from engin._dependency import Dependency, Invoke, Provide, Supply
from engin._lifecycle import Lifecycle
from engin._type_utils import TypeId

LOG = logging.getLogger("engin")

Option: TypeAlias = Invoke | Provide | Supply | Block
_Opt: TypeAlias = Invoke | Provide | Supply

_OS_IS_WINDOWS = os.name == "nt"


class Engin:
    """
    The Engin class runs your application. It assembles the required dependencies, invokes
    any invocations and manages your application's lifecycle.

    Examples:
        ```python
        import asyncio

        from httpx import AsyncClient

        from engin import Engin, Invoke, Provide


        def httpx_client() -> AsyncClient:
            return AsyncClient()


        async def main(http_client: AsyncClient) -> None:
            print(await http_client.get("https://httpbin.org/get"))

        engin = Engin(Provide(httpx_client), Invoke(main))

        asyncio.run(engin.run())
        ```
    """

    _LIB_OPTIONS: ClassVar[list[Option]] = [Provide(Lifecycle)]

    def __init__(self, *options: Option) -> None:
        self._providers: dict[TypeId, Provide] = {TypeId.from_type(Engin): Provide(self._self)}
        self._invokables: list[Invoke] = []

        self._stop_requested_event = Event()
        self._stop_complete_event = Event()
        self._exit_stack: AsyncExitStack = AsyncExitStack()
        self._shutdown_task: Task | None = None
        self._run_task: Task | None = None

        self._destruct_options(chain(self._LIB_OPTIONS, options))
        self._assembler = Assembler(self._providers.values())

    @property
    def assembler(self) -> Assembler:
        return self._assembler

    async def run(self) -> None:
        """
        Run the Engin and wait for it to be stopped via an external signal or by calling
        the `stop` method.
        """
        await self.start()
        self._run_task = asyncio.create_task(_raise_on_stop(self._stop_requested_event))
        await self._stop_requested_event.wait()
        await self._shutdown()

    async def start(self) -> None:
        """
        Starts the engin, this method waits for the shutdown lifecycle to complete.
        """
        LOG.info("starting engin")
        assembled_invocations: list[AssembledDependency] = [
            await self._assembler.assemble(invocation) for invocation in self._invokables
        ]

        for invocation in assembled_invocations:
            try:
                await invocation()
            except Exception as err:
                name = invocation.dependency.name
                LOG.error(f"invocation '{name}' errored, exiting", exc_info=err)
                return

        lifecycle = await self._assembler.get(Lifecycle)

        try:
            for hook in lifecycle.list():
                await self._exit_stack.enter_async_context(hook)
        except Exception as err:
            LOG.error("lifecycle startup error, exiting", exc_info=err)
            await self._exit_stack.aclose()
            return

        LOG.info("startup complete")

        self._shutdown_task = asyncio.create_task(self._shutdown_when_stopped())

    async def stop(self) -> None:
        """
        Stops the engin, this method waits for the shutdown lifecycle to complete.
        """
        self._stop_requested_event.set()
        await self._stop_complete_event.wait()

    async def _shutdown(self) -> None:
        LOG.info("stopping engin")
        await self._exit_stack.aclose()
        self._stop_complete_event.set()
        LOG.info("shutdown complete")

    async def _shutdown_when_stopped(self) -> None:
        await self._stop_requested_event.wait()
        await self._shutdown()

    def _destruct_options(self, options: Iterable[Option]) -> None:
        for opt in options:
            if isinstance(opt, Block):
                self._destruct_options(opt)
            if isinstance(opt, Provide | Supply):
                existing = self._providers.get(opt.return_type_id)
                self._log_option(opt, overwrites=existing)
                self._providers[opt.return_type_id] = opt
            elif isinstance(opt, Invoke):
                self._log_option(opt)
                self._invokables.append(opt)

    @staticmethod
    def _log_option(opt: Dependency, overwrites: Dependency | None = None) -> None:
        if overwrites is not None:
            extra = f"\tOVERWRITES {overwrites.name}"
            if overwrites.block_name:
                extra += f" [{overwrites.block_name}]"
        else:
            extra = ""
        if isinstance(opt, Supply):
            LOG.debug(f"SUPPLY      {opt.return_type_id!s:<35}{extra}")
        elif isinstance(opt, Provide):
            LOG.debug(f"PROVIDE     {opt.return_type_id!s:<35} <- {opt.name}() {extra}")
        elif isinstance(opt, Entrypoint):
            type_id = opt.parameter_types[0]
            LOG.debug(f"ENTRYPOINT  {type_id!s:<35}")
        elif isinstance(opt, Invoke):
            LOG.debug(f"INVOKE      {opt.name:<35}")

    def _self(self) -> "Engin":
        return self


class _StopRequested(RuntimeError):
    pass


async def _raise_on_stop(stop_requested_event: Event) -> None:
    """
    This method is based off of the Temporal Python SDK's Worker class:
    https://github.com/temporalio/sdk-python/blob/main/temporalio/worker/_worker.py#L488
    """
    try:
        # try to gracefully handle sigint/sigterm
        if not _OS_IS_WINDOWS:
            loop = asyncio.get_running_loop()
            for signame in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(signame, stop_requested_event.set)

            await stop_requested_event.wait()
            raise _StopRequested()
        else:
            should_stop = False

            # windows does not support signal_handlers, so this is the workaround
            def ctrlc_handler(sig: int, frame: FrameType | None) -> None:
                nonlocal should_stop
                if should_stop:
                    raise KeyboardInterrupt("Forced keyboard interrupt")
                should_stop = True

            signal.signal(signal.SIGINT, ctrlc_handler)

            while not should_stop:
                # In case engin is stopped via external `stop` call.
                if stop_requested_event.is_set():
                    return
                await asyncio.sleep(0.1)

            stop_requested_event.set()
    except asyncio.CancelledError:
        pass
