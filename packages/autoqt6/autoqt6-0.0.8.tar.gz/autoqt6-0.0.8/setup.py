# -*- coding: utf_8 -*-
from setuptools import setup

from autoqt6 import VERSION


with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='autoqt6',
    version=VERSION,
    description='Simplify pyqtProperty creation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
    ],
    keywords='PyQt,PyQt6,pyqtProperty,PySide6',
    author='NaKyle Wright, Jared Jones',
    author_email='jared.randall.jones@gmail.com',
    url='https://github.com/jrj99/autoqt6/',
    py_modules=['autoqt6'],
    python_requires='>=3.6',
    install_requires=[],
)
