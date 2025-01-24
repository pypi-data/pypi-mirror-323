# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='trajectronpp',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy==1.16.4',
        'pandas==0.25.1',
        'scipy==1.3.1',
        'seaborn==0.9.0',
        'tensorboard==1.14.0',
        'tensorboardX==1.8',
        'tensorflow==1.14.0',
        'tensorflow-estimator==1.14.0',
        'torch==1.4.0',
        'pyquaternion==0.9.5',
        'pytest==5.3.0',
        'orjson==2.1.4',
        'ncls==0.0.51',
        'dill==0.3.1.1',
        'tqdm==4.45.0',
        'notebook==6.0.3',
        'scikit-learn==0.22.1',
        'opencv-python==4.1.1.26',
        'nuscenes-devkit==1.0.6',
    ],
    author='Matheus Vargas Volpon Berto',  
    author_email='matheusvolpon.berto@gmail.com',
    description='A library for the Trajectron++ method, proposed by Tim Salzmann, Boris Ivanovic, Punarjay Chakravarty, and Marco Pavone in the entitled paper Trajectron++: Dynamically-Feasible Trajectory Forecasting With Heterogeneous Data',
    url='https://github.com/StanfordASL/Trajectron-plus-plus',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
