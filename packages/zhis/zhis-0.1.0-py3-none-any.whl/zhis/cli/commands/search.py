from functools import partial
from typing import List, Optional

import click
from peewee import ModelSelect

from zhis.__version__ import __version__
from zhis.config import Config
from zhis.db import History, database_connection
from zhis.gui import Gui, Mode, SelectedCommandResponse

from ..options.filter import (
    cwd_filter_option,
    exit_code_filter_option,
    tmux_session_filter_option,
)


@click.command("search", help="Interactive history search.")
@click.argument("KEYWORDS", nargs=-1)
@tmux_session_filter_option
@exit_code_filter_option
@cwd_filter_option
@click.option("-i", "--interactive", is_flag=True, help="Open interactive search GUI.")
@click.option(
    "-I",
    "--interactive-inline",
    is_flag=True,
    help="Open interactive search GUI in inline mode.",
)
@click.option(
    "--limit",
    default=None,
    type=int,
    help="Limit the number of search results.",
)
@click.option(
    "--offset",
    default=None,
    type=int,
    help="Offset the number of search results.",
)
@click.pass_obj
def search_command(
    config: Config,
    keywords: List[str],
    tmux_session: str,
    cwd: str,
    exit_code: int,
    interactive: bool,
    interactive_inline: bool,
    limit: Optional[int],
    offset: Optional[int],
):
    with database_connection():
        pattern = " ".join(keywords)

        query = History.query_history(
            pattern=pattern,
            tmux_session_context=tmux_session,
            path_context=cwd,
            exit_code=exit_code,
            limit=limit,
            offset=offset,
        )

        if interactive or interactive_inline:
            response = Gui(
                config.gui,
                query_callback=partial(History.query_history, base_query=query),
                version=__version__,
            ).run(inline=interactive_inline or config.gui.mode == Mode.INLINE)
        else:
            response = query

        if isinstance(response, SelectedCommandResponse):
            click.echo(f"__zhis_accept__:{response.command}")
        elif isinstance(response, History):
            click.echo(response.command)
        elif isinstance(response, ModelSelect):
            for history in list(response):
                click.echo(history.command)
