import click


@click.group("init", help="Print shell init script.")
def init_command():
    pass


@init_command.command("zsh")
def init_zsh_command():
    with open("shell/zhis.zsh", "r", encoding="utf-8") as file:
        for line in file:
            click.echo(line.strip("\n"))
