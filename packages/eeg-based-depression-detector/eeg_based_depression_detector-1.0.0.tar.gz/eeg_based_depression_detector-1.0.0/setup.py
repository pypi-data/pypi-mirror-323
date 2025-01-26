# setup.py
from setuptools import setup, find_packages

setup(
    name="eeg_based_depression_detector",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'eeg_based_depression_detector': ['data/*.pkl']
    },
    install_requires=[
        'numpy>=1.20.0',
        'scipy>=1.6.0',
        'scikit-learn>=1.0.0',
        'networkx>=3.0',
        'node2vec>=0.4.6',
        'gensim>=4.0.0',
        'joblib>=1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'eeg_based_depression_detector=eeg_based_depression_detector.predictor:main'
        ]
    },
    author="Yujie Huang",
    description="eeg-based Depression Detection System",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown'
)