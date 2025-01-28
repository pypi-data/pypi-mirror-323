import sys
import sh
import click

def run_command(cmd, fail_on_nonzero_exit_code=True):
    try:
        process = sh.Command(cmd[0])(*cmd[1:], _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _bg=True, _bg_exc=False)
        process.wait()
    except sh.ErrorReturnCode as e:
        if fail_on_nonzero_exit_code:
            click.echo(click.style(f"Error: external command `{cmd}` returned {e.exit_code}, exiting", fg='bright_red'))
            sys.exit()
    return process.exit_code
