# encoding: utf-8
from distutils.core import setup
import os
import re
import sys

if any(a == 'bdist_wheel' for a in sys.argv):
    from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'kexpect', '__init__.py'), 'r') as f:
    for line in f:
        version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", line)
        if version_match:
            version = version_match.group(1)
            break
    else:
        raise Exception("couldn't find version number")

long_description = """
Pexpect like-module to interact with Kubernetes based container\'s shell.
"""

REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            for_specifier = EXTRAS.setdefault(':{}'.format(specifier), [])
            for_specifier.append(requirement)
        else:
            REQUIRES.append(line)

setup(name='kexpect',
    version=version,
    packages=['kexpect'],
    description='Pexpect like-module to interact with Kubernetes based container\'s shell',
    long_description=long_description,
    author='Sunil Kumar S. B',
    author_email='skumarsb@cisco.com',
    license='Apache License Version 2.0',
    platforms='UNIX',
    classifiers = [
    ],
    install_requires=REQUIRES,
)
