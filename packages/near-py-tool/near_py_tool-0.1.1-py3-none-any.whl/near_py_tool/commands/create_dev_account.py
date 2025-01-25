import click
from rich_click import RichCommand


# todo: implement subcommands or manual prompts for cargo near args

@click.command(cls=RichCommand)
@click.option('--locked', is_flag=True)
@click.option('--no-doc', is_flag=True)
@click.option('--compact-abi', is_flag=True)
@click.option('--out-dir', metavar='<OUT_DIR>')
@click.option('--manifest-path', metavar='<MANIFEST_PATH>')
def create_dev_account(locked, no_doc, compact_abi, out_dir, manifest_path):
    """Create a development account using the faucet service sponsor to receive some NEAR tokens (testnet only) """
    pass