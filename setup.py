import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


def package_files(directory):
    paths = []
    for (root, dirs, files) in os.walk(directory):
        for file_item in files:
            paths.append(os.path.join(os.pardir, root, file_item))
    return paths


name = 'collection_stats'
version = '0.2.0'


setup(
    name=name,
    version=version,
    packages=[name, ],
    package_data={name: package_files(name)},
    zip_safe=False,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'collection-stats=collection_stats.entrypoint:main',
        ],
    },
    cmdclass={
        'install': install,
        'develop': develop,
    },
    install_requires=[
        'click>=7.1.2,<7.2.0',
        'xmltodict>=0.12.0,<0.13.0',
        'xmlschema>=1.2.5,<1.3',
    ],
)
