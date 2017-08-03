import os
from setuptools import setup, find_packages
import sys

version = "1.01"

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

setup(
    name='python-regparse',
    version=version,
    packages=find_packages(),
    license='MIT',
    author='Patrick Olsen',
    author_email='patrick.olsen@sysforensics.org',
    package_data={'regparse': ['*.plugin']},
    install_requires=[
        'Jinja2',
        'python-registry'
    ],
    entry_points={
        'console_scripts': ['regparse=regparse.command_line:main']
    },
    include_package_data=True
)
