from setuptools import setup
from pathlib import Path

long_description = (Path(__file__).parent/'README.md').read_text()
setup(
    name='weekdaytime',
    version='0.0.10',
    description='Python library that models available periods in a week',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Aaron Cheung',
    packages=['weekdaytime'],
    python_requires='>=3.6',
    install_requires=[
        'bitarray==2.7'
    ],
    zip_safe=False
)