import asyncio
import logging
import signal
from abc import ABC, abstractmethod

# TODO: implement configuration class -> checkout heisskleber config
from .config import ServiceConf


class Service(ABC):
    """BaseClass of a Service."""

    _running: bool = False
    logger: logging.Logger
    task: asyncio.Task[None]

    def __init__(self, config: ServiceConf) -> None:
        self.name = config.name
        self.logger = logging.getLogger(self.name)
        self.add_signal_handlers()

    def add_signal_handlers(self) -> None:
        """Add signal handler for SIGINT and SIGTERM."""
        loop = asyncio.get_event_loop()

        async def shutdown(sig: signal.Signals) -> None:
            tasks = []
            for task in asyncio.all_tasks(loop):
                if task is not asyncio.current_task():
                    task.cancel()
                    tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=False)
            self.logger.info("Program crashed successfully.")
            loop.stop()

        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig)))  # noqa: B023

    def start_hook(self) -> None:
        """Method to be implemented in derived classes, executed upon."""
        self.logger.info("Starting %s service", self.name)

    def stop_hook(self) -> None:
        """Method to be implemented in derived classes, executed upon exit."""
        self.logger.info("Stopping %s service", self.name)

    def exit_hook(self) -> None:
        """Method to be implemented in derived classes, executed upon SIGINT."""
        self.logger.info("Exiting %s service", self.name)

    def exception_hook(self) -> None:
        """Method to be implemented in derived classes, executed upon an exception."""
        self.logger.exception("Exception in %s service", self.name)

    @abstractmethod
    async def runner(self) -> None:
        """Core logic method, to be implemented in derived class.

        Needs to be a loop running forever to make sense.
        """

    def start(self) -> None:
        """Start the service."""
        self.task = asyncio.create_task(self.runner())

    def stop(self) -> None:
        """Stop the service."""
        self.stop_hook()
        self.logger.info("Stopping %s service", self.name)
