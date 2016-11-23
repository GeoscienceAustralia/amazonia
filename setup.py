#!/usr/bin/python3

from setuptools import setup

setup(
    name='amazonia',
    version='1.4.12',
    description="GA AWS CloudFormation creation library",
    author="The Geoscience Australia Autobots, and Lazar Bodor",
    author_email="autobots@ga.gov.au , lazar.bodor@ga.gov.au",
    url="https://github.com/GeoscienceAustralia/amazonia",
    license="New BSD license",
    packages=['amazonia'],
    install_requires=[
        'troposphere',
        'nose',
        'boto3',
        'pyyaml',
        'cerberus',
        'flask',
        'flask_cors',
        'inflection'
    ]
)
