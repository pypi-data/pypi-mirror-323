from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="time_checker",
    version="0.0.3",
    description="A reusable timer utility for Python scripts",
    long_description=long_description,  # Add this line
    long_description_content_type="text/markdown",  # Specify README format
    author="Deep Korat",
    author_email="deepkorat13@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
