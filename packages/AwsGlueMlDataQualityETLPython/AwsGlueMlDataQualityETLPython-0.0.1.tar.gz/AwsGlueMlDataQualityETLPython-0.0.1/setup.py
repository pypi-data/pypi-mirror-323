import sys
from setuptools import setup

args = ' '.join(sys.argv).strip()
if not any(args.endswith(suffix) for suffix in ['setup.py sdist', 'setup.py check -r -s']):
    raise ImportError('This package is parked by AWS Glue.')

setup(
    name='AwsGlueMlDataQualityETLPython',
    author='awsglue',
    version='0.0.1',
    description='This package is parked by AWS Glue.',
    classifiers=[
        'Development Status :: 7 - Inactive',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ]
)
