"""Console script for uptainer."""

import typer
import structlog
import logging
from pathlib import Path
from typing import Annotated
from uptainer.loader import Loader
from structlog.contextvars import merge_contextvars
from os import getenv

app = typer.Typer()


@app.command()
def main(  # noqa D417
    config_file: Annotated[Path, typer.Option(help="Configuration file")] = "config.yml",
    debug: Annotated[bool, typer.Option(help="Enable Debug logging")] = False,
) -> None:
    """Main CLI function for uptainer project.

    Args:
        config (Path): Configuration file with PATH class.

    Returns:
        None
    """
    if debug:
        LOGLEVEL = logging.DEBUG
    else:
        LOGLEVEL = logging.INFO

    if getenv("UPTAINER_DEBUG", "0") == "1":
        LOGLEVEL = logging.DEBUG

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="%d/%m/%Y %H:%M:%S", utc=False),
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            merge_contextvars,
            structlog.processors.EventRenamer("msg"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(LOGLEVEL),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger()

    if not config_file.is_file():
        log.error("The config file seems not valid.")
        raise typer.Abort()
    loader = Loader(log=log, config_file=config_file)
    loader.run()


if __name__ == "__main__":
    app()
