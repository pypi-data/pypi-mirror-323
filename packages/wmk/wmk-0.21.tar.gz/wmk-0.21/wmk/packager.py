import subprocess
import os
import logging
import json
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

class Packager:
    """
    A class for packaging Python dependencies and project files into a distributable archive.

    The Packager handles downloading platform-specific Python packages, generating build manifests,
    and creating ZIP archives containing the project and its dependencies.

    Args:
        target (str, optional): Target directory path. Defaults to current working directory.
        platform (str, optional): Target platform for packages. Defaults to "manylinux2014_x86_64".
        only_tracked (bool, optional): Include only git-tracked files. Defaults to True.
        additional_files (list, optional): Additional files/directories to include in the archive.
        build_version (str, optional): Version identifier for the build.
        python_version (str, optional): Target Python version for packages.

    Attributes:
        target_dir (str): Directory where the packaging operations take place
        platform (str): Target platform identifier
        only_tracked (bool): Flag to include only git-tracked files
        additional_files (list): List of additional files to include
        build_version (str): Build version identifier
        python_version (str): Target Python version
        dependencies_dir (str): Directory for downloaded dependencies
        logger (Logger): Logger instance for the class
    """
    
    def __init__(self, target=None, platform="manylinux2014_x86_64", only_tracked=True, additional_files=None, 
                 build_version=None, python_version=None):
        self.target_dir = target or os.getcwd()
        self.platform = platform
        self.only_tracked = only_tracked
        self.additional_files = additional_files
        self.build_version = build_version
        self.python_version = python_version
        self.dependencies_dir = os.path.join(self.target_dir, 'dependencies')
        self.logger = logging.getLogger(__name__)

    def download_packages(self):
        """
        Download packages with specific platform constraints.

        This method looks for dependency specifications in requirements.txt, pyproject.toml,
        or setup.py and downloads all required packages using pip. Downloads are platform-specific
        and stored in the dependencies directory.

        Returns:
            bool: True if packages were downloaded successfully, False otherwise.

        Raises:
            FileNotFoundError: If no dependency specification file is found.
        """
        try:
            # Ensure dependencies directory exists
            Path(self.dependencies_dir).mkdir(parents=True, exist_ok=True)
            
            # Check for different dependency specification files
            # and construct the appropriate pip download command
            requirements_path = os.path.join(self.target_dir, 'requirements.txt')
            has_requirements_txt = os.path.exists(requirements_path)
            has_other_configs = os.path.exists(os.path.join(self.target_dir, 'pyproject.toml')) or os.path.exists(os.path.join(self.target_dir, 'setup.py'))
            dependencies_params = ['-r', requirements_path] if has_requirements_txt else ['.'] if has_other_configs else None
            if not dependencies_params:
                raise FileNotFoundError(f"No dependency specification file found (requirements.txt, pyproject.toml, or setup.py)")
            
            python_version_params = ['--python-version', self.python_version] if self.python_version else []
            
            self.logger.info("Downloading packages...")
            cmd = [
                'pip', 'download',
                *dependencies_params,
                '-d', self.dependencies_dir,
                '--platform', self.platform,
                *python_version_params,
                '--only-binary=:all:'
            ]

            # Execute pip download command
            return self.download_with_output(cmd)
        
        except Exception as e:
            self.logger.error(f"Download packages unexpected error: {e}")
            return False
    
    def generate_manifest(self):
        """
        Generate a manifest file containing package metadata.

        Creates a JSON manifest containing build timestamp, runtime requirements,
        and other metadata about the package.

        Returns:
            dict: A dictionary containing the manifest data with the following structure:
                {
                    "timeStamp": str,
                    "entities": list,
                    "runtime": str,
                    "runtimeRequirements": dict,
                    "buildVersion": str
                }
        """
        manifest = {
            "timeStamp": datetime.now().isoformat(),
            "entities": [],
            "runtime": "python",
            "runtimeRequirements": {
                "platform": self.platform,
                "pythonVersion": self.python_version or "",
            },
            # TODO: Support pyproject.toml and setup.py
            "scripts": {
                "install": "pip install --no-index --find-links dependencies/ -r requirements.txt"
            },
            "buildVersion": self.build_version or "",
        }
        
        self.logger.info("Manifest generated successfully")
        return manifest

    def create_archive(self, archive_name):
        """
        Create a ZIP archive of the downloaded packages and project files.

        Args:
            archive_name (str): Name of the archive file to create

        Returns:
            bool: True if archive was created successfully, False otherwise.

        The archive includes:
            - All specified project files (git-tracked or all, based on only_tracked)
            - Downloaded dependencies
            - Additional files specified during initialization
            - BuildManifest.json containing package metadata
        """
        try:
            dir_to_archive = Path(self.target_dir)
            archive_path = os.path.join(self.target_dir, archive_name)
            
            # Generate manifest as JSON string
            manifest = self.generate_manifest()
            manifest_str = json.dumps(manifest, indent=2)

            if self.only_tracked:
                # Get tracked files using git
                files = subprocess.check_output(
                    ['git', 'ls-files', '--exclude-standard'],
                    cwd=dir_to_archive,
                    text=True
                ).splitlines()
            else:
                # Get all files in the directory
                files = self._get_nested_files(dir_to_archive, dir_to_archive)
            
            # Add dependencies directory
            if os.path.exists(self.dependencies_dir):
                dependencies_files = self._get_nested_files(self.dependencies_dir, dir_to_archive)
                files.extend(file for file in dependencies_files if file not in files)
            
            # Add additional files
            if self.additional_files:
                for path in self.additional_files:
                    full_path = os.path.join(dir_to_archive, path)
                    if os.path.isfile(full_path):
                        files.append(path)
                    elif os.path.isdir(full_path):
                        additional_files = self._get_nested_files(full_path, dir_to_archive)
                        files.extend(additional_files for file in additional_files if file not in files)

            with ZipFile(archive_path, 'w') as zip_file:
                # Add manifest directly as string
                zip_file.writestr('Build/BuildManifest.json', manifest_str)
                
                # Add files
                for file in files:
                    file_path = os.path.join(dir_to_archive, file)
                    zip_path = os.path.join('Build', file)
                    zip_file.write(file_path, zip_path)

            self.logger.info(f"Archive created successfully: {archive_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating archive: {e}")
            return False

    def _get_nested_files(self, target_dir, base_dir):
        """
        Recursively get all files in a directory relative to a base directory.

        Args:
            target_dir (str): Directory to scan for files
            base_dir (str): Base directory for creating relative paths

        Returns:
            list: List of relative file paths
        """
        files = []
        for root, _, filenames in os.walk(target_dir):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), base_dir)
                files.append(rel_path)
        return files

    def download_with_output(self, cmd):
        """
        Run the download command and print warnings and errors in real-time.
        
        Args:
            cmd (list): download command and arguments
        """
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1,
            )
            
            while True:
                stderr_line = process.stderr.readline()
                if stderr_line:
                    if 'warning' in stderr_line.lower():
                        self.logger.warning(stderr_line.strip())
                    elif 'error' in stderr_line.lower():
                        self.logger.error(stderr_line.strip())
                    else:
                        # Catch-all for other stderr content
                        self.logger.error(stderr_line.strip())
                
                # Check if process is complete
                if stderr_line == '' and process.poll() is not None:
                    break
            
            if process.returncode == 0:
                self.logger.info("Package download completed successfully")
                return True

        except Exception as e:
            self.logger.error(f"Error in running download command: {e}")
            return False
