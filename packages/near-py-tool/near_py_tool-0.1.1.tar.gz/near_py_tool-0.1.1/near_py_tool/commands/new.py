import click
from rich_click import RichCommand
import os
import shutil
from importlib.resources import files
import toml

@click.command(cls=RichCommand)
@click.argument('project_dir')
def new(project_dir):
    """Initializes a new project to create a contract"""
    new_project_template = files('near_py_tool') / 'assets' / 'new-project-template'
    project_abs_path = os.path.abspath(project_dir)

    if os.path.isdir(project_abs_path):
        click.echo('Error:')
        click.echo(click.style(f'   Destination `{project_abs_path}` already exists. Refusing to overwrite existing project.', fg='bright_red'))
        return
    
    os.makedirs(project_abs_path, exist_ok=True)
    for item in os.listdir(new_project_template):
        src_item = os.path.join(new_project_template, item)
        dst_item = os.path.join(project_abs_path, item)
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item)
        else:
            shutil.copy2(src_item, dst_item)

    pyproject = toml.load(new_project_template / 'pyproject.toml')
    pyproject['project']['name'] = os.path.basename(project_dir)
    with open(f"{project_abs_path}/pyproject.toml", "w") as f:
      toml.dump(pyproject, f)

    click.echo(f"""
New project is created at '{project_abs_path}'.

Now you can build, test, and deploy your project using near-py-tool:
 * `near-py-tool build`
 * `near-py-tool deploy`
""")
#Your new project has preconfigured automations for CI and CD, just configure `NEAR_CONTRACT_STAGING_*` and `NEAR_CONTRACT_PRODUCTION_*` variables and secrets on GitHub to enable automatic deployment to staging and production. See more details in `.github/workflow/*` files.
#""")
