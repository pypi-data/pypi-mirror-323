# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='trajectron',
    version='0.1.3',
    packages=find_packages(include=['trajectron', 'trajectron.*']),
    install_requires=open('requirements.txt').read().splitlines(),
    include_package_data=True,
    license='MIT',
    author='Matheus Vargas Volpon Berto',  
    author_email='matheusvolpon.berto@gmail.com',
    description='A unofficial library for the Trajectron++ method, proposed by Tim Salzmann, Boris Ivanovic, Punarjay Chakravarty, and Marco Pavone in the entitled paper Trajectron++: Dynamically-Feasible Trajectory Forecasting With Heterogeneous Data.',
    url='https://github.com/StanfordASL/Trajectron-plus-plus',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)