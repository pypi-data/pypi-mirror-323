from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')  # Ensure UTF-8 encoding

setup(
    name='topsis-Aryan-7019',  # Package name
    version='0.0.1',  # Follow semantic versioning
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'openpyxl'
    ],
    author='Aryan',
    author_email='asharma27_be22@thapar.edu',
    description='A Python package implementing the TOPSIS method',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    project_urls={
        'Source Repository': 'https://github.com/aryansharma19992e/topsis'
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
