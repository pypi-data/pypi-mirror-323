"""
Pip.Agents Commons
--------------------

Pip.Agents is an open-source toolkit for AI applications.
pip_agents_core package provides core AI abstractions.

Links
`````

* `website <http://github.com/pip-agents/pip-agents>`
* `development version <http://github.com/pip-agents-python/pip-agents-core-python>`

"""

from setuptools import find_packages
from setuptools import setup

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='pip_agents_core',
    version='0.0.2',
    url='https://github.com/pip-agents/pip-agents-python/tree/main/pip-agents-core-python',
    license='MIT',
    description='Core abstractions for Pip.Agents in Python',
    author='Enterprise Innovation Consulting',
    author_email='seroukhov@gmail.com',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'iso8601',
        'pytz'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
