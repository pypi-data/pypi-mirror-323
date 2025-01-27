import click
from .packager import Packager
from .loader import Loader
import logging

logging.basicConfig(
    level=logging.NOTSET,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@click.group()
def cli():
    """WMK CLI tool"""
    pass

@cli.command()
@click.option(
    '-t',
    '--target', 
    required=False,
    default=None,
    help='Directory containing requirements.txt and where packages will be stored'
)
@click.option(
    '-n',
    '--name',
    required=False,
    default='Build.zip',
    help='Name of the output ZIP file'
)
@click.option(
    '-p',
    '--platform',
    required=False,
    default='manylinux2014_x86_64',
    help='Target platform for dependencies'
)
@click.option(
    '--only-tracked',
    required=False,
    default=True,
    help='Skip files listed in .gitignore'
)
@click.option(
    '-a',
    '--additional-files',
    required=False,
    multiple=True,
    help='Additional files for the archive'
)
@click.option(
    '-v',
    '--build-version',
    required=False,
    default=None,
    help='Version of the build'
)
@click.option(
    '--python-version',
    required=False,
    default=None,
    help='Python version to use'
)
def package(target, name, platform, only_tracked, additional_files, build_version, python_version):
    """Download Python packages and create archive"""
    packager = Packager(target, platform, only_tracked, additional_files, build_version, python_version)
    if packager.download_packages():
        packager.create_archive(name)
    else:
        packager.logger.error("Skipping archive creation due to download errors")

@cli.command()
@click.option(
    '-u',
    '--url',
    required=True,
    help='URL of the file to download'
)
@click.option(
    '-f',
    '--filepath',
    required=True,
    help='Local path where to save the file'
)
def download(url, filepath):
    """Download a file from URL to local path"""
    transfer = Loader()
    transfer.download_file(url, filepath)

if __name__ == '__main__':
    cli()