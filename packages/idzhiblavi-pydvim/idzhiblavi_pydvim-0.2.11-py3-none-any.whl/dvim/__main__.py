#!/usr/bin/env python3

import click
from dvim.runner import Runner


@click.command()
@click.option("--debug/--no-debug", default=False)
@click.option("--executable", default="nvim")
@click.option("--workspace", default=None)
@click.option("--session", default=None)
@click.option(
    "--action",
    type=click.Choice(
        ["start-local", "start-headless", "start-server", "remote", "send", "attach"]
    ),
    required=True,
)
@click.argument("args", nargs=-1)
def cli(debug, executable, workspace, session, action, args):
    runner = Runner(debug, executable, workspace, session)

    if action == "start-local":
        runner.local(args)
    elif action == "start-headless":
        runner.headless(args)
    elif action == "start-server":
        runner.server(args)
    elif action == "remote":
        runner.remote(args)
    elif action == "send":
        runner.send(args)
    elif action == "attach":
        runner.attach(args)
    else:
        raise RuntimeError(f"Unsupported action: {action}")


def cli_entrypoint():
    cli()


if __name__ == "__main__":
    cli_entrypoint()
