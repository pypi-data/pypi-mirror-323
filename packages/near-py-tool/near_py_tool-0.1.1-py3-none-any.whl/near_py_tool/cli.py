import click
from rich_click import RichGroup
from near_py_tool.commands.new import new
from near_py_tool.commands.build import build
from near_py_tool.commands.abi import abi
from near_py_tool.commands.create_dev_account import create_dev_account
from near_py_tool.commands.deploy import deploy

@click.group(cls=RichGroup)
def cli():
    """Python NEAR contract build/deploy tool"""
    pass

cli.add_command(new)
cli.add_command(build)
cli.add_command(abi)
cli.add_command(create_dev_account)
cli.add_command(deploy)

if __name__ == "__main__":
    cli()
