#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Distribution
try:
    from setuptools_rust import RustExtension, Binding
except ImportError:
    import subprocess
    print("\nsetuptools_rust is required before install - https://pypi.python.org/pypi/setuptools-rust")
    print("attempting to install with pip...")
    print(subprocess.check_output(["pip", "install", "setuptools_rust"]))
    from setuptools_rust import RustExtension

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'cffi>=1.0.0',
    # TODO: put package requirements here
]

test_requirements = [
    'pytest>=2.9.2',
    'pytest-runner>=2.0'
]

setup(
    name='roll_regression',
    version='0.1.0',
    description="A fast rolling regression library in Python",
    long_description=readme + '\n\n' + history,
    author="Gavin Chan",
    author_email='gavincyi@gmail.com',
    url='https://github.com/gavincyi/roll_regression',
    packages=[
        'roll_regression',
    ],
    package_dir={'roll_regression':
                 'roll_regression'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    rust_extensions=[
        RustExtension('roll_regression', 'roll_regression/rust/Cargo.toml',
                       debug=False, binding=Binding.NoBinding)],
    keywords='roll_regression',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=['setuptools_rust',
    'pytest-runner>=2.0',
    ]
)
