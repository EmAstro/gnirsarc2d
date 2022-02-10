# !usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
import os
import glob


def get_scripts():
    r"""Grab scripts in the bin directory and in the sub-folder.
    """
    scripts = []
    if os.path.isdir('bin'):
        scripts = [script_name for script_name in glob.glob(os.path.join('bin', '*'))
                   if not os.path.basename(script_name).endswith('.rst') and not os.path.isdir(script_name)]
    return scripts


def get_requirements():
    r"""Get requirements from a system file.
    """
    name = 'gnirsarc2d/requirements.txt'
    requirements_file = os.path.join(os.path.dirname(__file__), name)
    install_requires = [line.strip().replace('==', '>=') for line in open(requirements_file)
                        if not line.strip().startswith('#') and line.strip() != '']
    return install_requires

from setuptools import setup, find_packages
NAME = 'gnirsarc2d'
VERSION = '0.0.0dev'
AUTHOR = 'Ema'


def run_setup(scripts, packages, install_requires):
    r"""Run the setup
    """
    setup(name=NAME,
          provides=NAME,
          version=VERSION,
          license='TBD',
          description='2D estimates of the wavelength solution of GNIRS data',
          long_description=open('README.md').read(),
          author='Ema',
          author_email='emanuele.farina@noirlab.edu',
          keywords='GNIRS astronomy GEMINI',
          url='https://github.com/EmAstro/gnirsarc2d',
          packages=packages,
          include_package_data=True,
          scripts=scripts,
          install_requires=install_requires,
          requires=['Python (>3.9.0)'],
          zip_safe=False,
          use_2to3=False,
          classifiers=[
              'Development Status :: 2 - Pre-Alpha',
              'Intended Audience :: Science/Research',
              'License :: TBD',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 3.9',
              'Topic :: Scientific/Engineering :: Astronomy',
              'Topic :: Software Development :: Libraries :: Python Modules',
              'Topic :: Software Development :: User Interfaces'
          ],
          )


if __name__ == '__main__':
    # Compile the scripts in the bin/ directory
    scripts = get_scripts()
    print(scripts)
    # Get the packages to include
    packages = find_packages()
    # Collate the dependencies based on the system text file
    install_requires = get_requirements()
    # Run setup from setuptools
run_setup(scripts, packages, install_requires)