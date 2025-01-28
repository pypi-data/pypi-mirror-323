# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol', 'exasol.bucketfs']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=23.2.0', 'exasol-saas-api>=0.3.0', 'httpx>=0.27.0', 'requests>=2.24.0']

setup_kwargs = {
    'name': 'exasol-bucketfs',
    'version': '1.0.1',
    'description': 'BucketFS utilities for the Python programming language',
    'long_description': 'Exasol Bucketfs\n###############\n\n.. image:: https://img.shields.io/pypi/v/exasol-bucketfs\n     :target: https://pypi.org/project/exasol-bucketfs/\n     :alt: PyPI Version\n\n.. image:: https://img.shields.io/pypi/pyversions/exasol-bucketfs\n    :target: https://pypi.org/project/sexasol-bucketfs\n    :alt: PyPI - Python Version\n\n.. image:: https://img.shields.io/badge/exasol-7.1.9%20%7C%207.0.18-green\n    :target: https://www.exasol.com/\n    :alt: Exasol - Supported Version(s)\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: Formatter - Black\n\n.. image:: https://img.shields.io/badge/imports-isort-ef8336.svg\n    :target: https://pycqa.github.io/isort/\n    :alt: Formatter - Isort\n\n.. image:: https://img.shields.io/pypi/l/exasol-bucketfs\n     :target: https://opensource.org/licenses/MIT\n     :alt: License\n\n.. image:: https://img.shields.io/github/last-commit/exasol/bucketfs-python\n     :target: https://pypi.org/project/exasol-bucketfs/\n     :alt: Last Commit\n\n\nExasol Bucketfs is a python library to interact with Exasol `Bucketfs-Service(s) <https://docs.exasol.com/db/latest/database_concepts/bucketfs/bucketfs.htm>`_.\n\n🚀 Features\n------------\n\n* List all buckets of a bucketfs service\n* List all files in a bucket\n* Download files from bucketfs\n* Upload files to bucketfs\n* Delete files from bucketfs\n* Pythonic API\n\n🔌️ Prerequisites\n-----------------\n\n- `Python <https://www.python.org/>`_ >= 3.8\n\n💾 Installation\n----------------\n\n.. code-block:: shell\n\n    pip install exasol-bucketfs\n\n📚 Documentation\n----------------\n\nThe latest documentation can be found `here <https://exasol.github.io/bucketfs-python/>`_.\n\n',
    'author': 'Torsten Kilias',
    'author_email': 'torsten.kilias@exasol.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/exasol/bucketfs-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
