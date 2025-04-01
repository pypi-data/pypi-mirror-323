import logging
import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Check if running in a conda environment
in_conda = 'CONDA_PREFIX' in os.environ

if in_conda:
    if not (3, 7) <= sys.version_info < (3, 12):
        logging.error('Python version not supported, python 3.7 to 3.11 is required. %f' , sys.version_info)
        sys.exit('Python version not supported, 3.7 to 3.11 is required.')

# Define common dependencies
common_requires = [
    'requests',
    'wget',
    'packaging<=24.0'
]

# Define extra dependencies for conda environments
conda_requires = ['psyneulink']

non_conda_requires = []

# Combine dependencies based on environment
install_requires = common_requires + (conda_requires if in_conda else non_conda_requires)

class Install(install):
    user_options = install.user_options + [
        ('path=', None, 'an option that takes a value')
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.path = None

    def finalize_options(self):
        # Validate options
        if self.path is None:
            self.path = os.path.dirname(os.path.realpath(__file__))
        super().finalize_options()

    def run(self):
        global path
        path = self.path # will be 1 or None

        package_name = 'psyneulinkviewer'
        
        # Try to uninstall the package using pip
        try:
            result = subprocess.run(
                ['pip', 'uninstall', '-y', package_name, "--break-system-packages"],
                capture_output=True,
                text=True,
                check=True
            )
            logging.info(f"Previous version of {package_name} uninstalled: {result.stdout}")
            
            # Purge pip cache after successful uninstall
            purge_result = subprocess.run(['pip', 'cache', 'purge'], capture_output=True, text=True)
            logging.info(f"Pip cache purged: {purge_result.stdout}")
        
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to uninstall {package_name}: {e.stderr}")
        
        # Run prerequisites from the psyneulinkviewer package
        from psyneulinkviewer.start import prerequisites
        prerequisites()
        install.run(self)

setup(
    name="psyneulinkviewer",
    version="0.5",
    url='https://github.com/metacell/psyneulinkviewer',
    author='metacell',
    author_email='dev@metacell.us',
    setup_requires=['requests',
                      'wget',
                      'packaging<=24.0'],
    install_requires=install_requires,
    packages=find_packages(),
    cmdclass={
        'install': Install
    },
    python_requires=">=3.7"
)
