from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='topsis-102203128',
    version='1.0.1',
    description='A Python package to calculate TOPSIS scores',
    long_description=long_description,  # Include the long description
    long_description_content_type='text/markdown',
    url="https://github.com/rishikam23/Topsis-Rishika-102203128",  # Specify Markdown as the content type
    author='Rishika Mathur',
    author_email="rmathur_be22@thapar.edu",
    packages=find_packages(),
    py_modules=['rishika_102203128'],  # Use the new module name
    install_requires=[
        'pandas',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'topsis=rishika_102203128:main',  # Update to use the new module and main function
        ],
    },
)
