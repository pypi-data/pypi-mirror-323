# setup.py
from setuptools import setup, find_packages

setup(
    name='NEIST_APG1',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'tensorflow',  # or any other dependencies
    ],
    description='A package for loading DNN models DNN_MS_NEIST_APG1 and DNN_NEIST_APG1',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    usage="from NEIST_APG1 import DNN_NEIST_APG1",
    author='Amit Kumar Pathak',
    author_email='arjunpthk@gmail.com',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
