import sys
from datetime import datetime
from pathlib import Path
from time import sleep

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from typing_extensions import Annotated

from dblocks_core import context, dbi, exc, writer
from dblocks_core.config import config
from dblocks_core.config.config import logger
from dblocks_core.git import git
from dblocks_core.model import config_model
from dblocks_core.parse import prsr_simple
from dblocks_core.script.workflow import cmd_deployment, cmd_extraction, cmd_init

app = typer.Typer(
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
)

console = Console()


@app.command()
def init():
    """Initialize current directory (git init, basic config files, gitignore)."""
    cmd_init.make_init()


@app.command()
def env_test_connection(environment: str):
    cfg = config.load_config()
    env = config.get_environment_from_config(cfg, environment)
    ext = dbi.extractor_factory(env)
    ext.test_connection()


@app.command()
def env_list():
    """Display list of configured environments."""
    cfg = config.load_config()

    console.print("These environments exist:", style="bold")

    table = Table(title="List of environments")
    for _h in ("environment name", "host", "user"):
        table.add_column(_h)
    for env_name, cfg in cfg.environments.items():
        table.add_row(env_name, cfg.host, cfg.username)
    console.print(table)


@app.command()
def env_extract(
    environment: Annotated[
        str,
        typer.Argument(
            help="Name of the environment you want to extract. "
            "The environment must be configured in dblocks.toml."
        ),
    ],
    *,
    since: Annotated[
        str | None,
        typer.Option(
            help="How long history do we want to process. "
            "Here you define the duration which will be substracted from current time "
            "to get the datetime, that is used to filter changes - only tables that "
            "were changed (or created) after this date will be extracted. "
            "Examples of the input you can use:\n"
            "commit (meaning since last commit date) "
            "1d (one day), "
            "2w (two weeks), "
            "3m (3 three months).",
        ),
    ] = None,
    assume_yes: Annotated[
        bool, typer.Option(help="Do not ask for confirmations.")
    ] = False,
    commit: Annotated[bool, typer.Option(help="Commit changes to the repo.")] = True,
    countdown_from: Annotated[
        int,
        typer.Option(
            help="Countdown untill start, after confirmation, "
            "if full extraction was requested."
        ),
    ] = 10,
    filter_databases: Annotated[
        str | None,
        typer.Option(
            help="Mask of databases that will be extracted. "
            "The '%' sign means 'any number of any characters'."
        ),
    ] = None,
    filter_names: Annotated[
        str | None,
        typer.Option(
            help="Mask of tables that will be extracted. "
            "The '%' sign means 'any number of any characters'."
        ),
    ] = None,
    filter_creator: Annotated[
        str | None,
        typer.Option(
            help="Mask of the user who created the object. "
            "The '%' sign means 'any number of any characters'."
        ),
    ] = None,
):
    """
    Extraction of the database based on an environment name. The extraction can be
    either full, or incremental, based on the --since flag.
    """
    cfg = config.load_config()

    # repo, check if it is dirty
    repo = git.repo_factory(raise_on_error=True)
    if repo is not None and repo.is_dirty():
        logger.warning("Repo is not clean!")
        console.print(
            "Repo is not clean!\n"
            "Extraction will not run, unless it is continuation of previously "
            "unfinished process.",
            style="bold red",
        )

    # attempt to get information about the history length
    since_dt: None | datetime = None
    if since is not None:
        if "commit" in since:
            if repo is None:
                raise exc.DOperationsError("git repo not found")
            since_dt = repo.last_commit_date()
            if since_dt is None:
                raise exc.DOperationsError("no commit found")
            since_dt = since_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            since_dt = prsr_simple.parse_duration_since_now(since)
        logger.info(
            "extract objects changed after: " + since_dt.strftime("%Y-%m-%d %H:%M:%S")
        )
    elif not assume_yes:
        really = Prompt.ask(
            "This process has a few risks:"
            "\n- it can run for a long time and could leave the repo in incosistent "
            "state."
            "\n- directories that represent databases which are subject to extraction"
            "will be dropped."
            "\n\nYou could run incremental extraction using --since flag instead."
            "\nIf this is the first time you run the xtraction, answer yes."
            "\nAre you sure you want to run this? (yes/no)",
            default="no",
        ).strip()
        if really != "yes":
            logger.error(f"action canceled by prompt: {really}")

            sys.exit(1)

        # countdown
        for i in range(countdown_from, -1, -1):
            console.print(f"{i} ...", style="bold red")
            sleep(1)

    env = config.get_environment_from_config(cfg, environment)
    ext = dbi.extractor_factory(env)
    wrt = writer.create_writer(env.writer)
    with context.FSContext(
        name="command-extract",
        directory=cfg.ctx_dir,
    ) as ctx:
        cmd_extraction.run_extraction(
            ctx=ctx,
            env=env,
            ext=ext,
            wrt=wrt,
            repo=repo,
            env_name=environment,
            filter_since_dt=since_dt,
            commit=commit,
            filter_databases=filter_databases,
            filter_names=filter_names,
            filter_creator=filter_creator,
        )
    ctx.done()


@app.command()
def env_deploy(
    environment: str,
    path: str,
    assume_yes: bool = False,
    countdown_from: int = 10,
):
    """
    Full deployment of a directory.
    This action is destructive to your DB schema (use only in dev/test env).
    """
    # prepare config
    cfg = config.load_config()
    env = config.get_environment_from_config(cfg, environment)
    deploy_dir = Path(path)

    # sanity check
    if not deploy_dir.is_dir():
        message = f"not a dir: {deploy_dir.as_posix()}"
        raise exc.DOperationsError(message)

    logger.warning("starting deployment")
    with context.FSContext(
        name=f"command-deploy-{environment}",
        directory=cfg.ctx_dir,
        no_exception_is_success=False,  # we have to confirm context deletion "by hand"
    ) as ctx:
        # make sure we know what is being done!
        if not assume_yes:
            _confirm_deployment(environment, deploy_dir, env, countdown_from, ctx)

        # point of no return
        ext = dbi.extractor_factory(env)
        failures = cmd_deployment.deploy_dir(
            deploy_dir,
            env=env,
            cfg=cfg,
            ctx=ctx,
            ext=ext,
        )

        cmd_deployment.make_report(cfg.report_dir, environment, failures)
        if len(failures) == 0:
            console.print("Successfull run", style="bold green")
            ctx.done()
        else:
            console.print("DONE with errors", style="bold red")
            console.print("We do NOT delete context.")


@app.command()
def cfg_check():
    """Checks configuration files, without actually doing 'anything'."""
    cfg = config.load_config()
    logger.info("OK")
    config.cfg_to_censored_json(cfg)
    # console.print_json()


@app.command()
def ctx_list():
    """List all contexts."""
    cfg = config.load_config()
    ctx_dir = cfg.ctx_dir

    if not ctx_dir.exists():
        logger.warning(f"context dir not found at {ctx_dir.resolve()}")
        ctx_dir = context.find_ctx_root(context_dir_name=ctx_dir.name)
        if ctx_dir is None:
            logger.error("failed to find context dir")
            sys.exit(1)
        else:
            logger.warning(f"assuming: {ctx_dir.resolve()}")

    files = []
    for ctx_file in ctx_dir.iterdir():
        if not ctx_file.is_file():
            continue
        if ctx_file.suffix != ".json":
            continue
        files.append(ctx_file)

    if len(files) == 0:
        console.print("No contexts found", style="bold red")

    console.print("These context files were found:", style="bold")
    for ctx_file in files:
        console.print(ctx_file.as_posix())


@app.command()
def ctx_drop(
    ctx: str,
):
    """Deletes a context"""
    config.load_config()
    ctx_file = Path(ctx)
    if not ctx_file.exists():
        logger.error(f"context does not exist: {ctx_file.as_posix()}")
        sys.exit(1)

    # confirm
    console.print(f"You are about to drop the context {ctx_file.as_posix()}.")
    really = Prompt.ask("Are you sure? (yes/no)", default="no").strip()
    if really != "yes":
        logger.error(f"action canceled by prompt: {really}")
        sys.exit(1)
    ctx_file.unlink()


def _confirm_deployment(
    environment: str,
    deploy_dir: Path,
    env: config_model.EnvironParameters,
    countdown_from: int,
    ctx: context.FSContext,
):
    ctx_len = len(ctx.ctx_data.checkpoints)

    # build params table
    params = Table(title="Parameters")
    params.add_column("parameter")
    params.add_column("value")
    for (
        k,
        v,
    ) in (
        ("environment", environment),
        ("directory", deploy_dir.as_posix()),
        ("env.host", env.host),
        ("env.username", env.username),
        ("# of actions that succeded before", str(ctx_len)),
    ):
        params.add_row(k, v)

    # printout of params
    if ctx_len > 0:
        console.print(
            "*** This is a restart of unfinished action ***",
            style="bold red",
        )
        console.print("Use the ctx-list command to see what contexts exist")
    else:
        console.print("This is a clean start", style="bold green")

    console.print("Deployment with these parameters:", style="bold")
    console.print(params)
    console.print("This is a destructive action.")
    console.print("- objects will be DROPPED")
    console.print("- objects will be CREATED")
    console.print("- in fact, we will try to sync target databases against metadata")
    console.print("  with NO regard to data safety !!!", style="bold red")
    console.print("=== STOP AND THINK! ===", style="bold red")
    console.print("If you answer 'yes', countdown will ensue.")
    console.print("You will have one last chance to cancel the operation.")

    # confirm
    really = Prompt.ask("Are you sure? (yes/no)", default="no").strip()
    if really != "yes":
        logger.error(f"action canceled by prompt: {really}")
        sys.exit(1)

    # countdown
    for i in range(countdown_from, -1, -1):
        console.print(f"{i} ...", style="bold red")
        sleep(1)


@exc.catch_our_errors()
def main():
    console.print(" dblc: ", style="bold blue", end="")
    console.print(" dblocks_core features", style="bold")
    app()


if __name__ == "__main__":
    main()
