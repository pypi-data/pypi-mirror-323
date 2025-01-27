
from setuptools import setup, find_packages

setup(
    name='Topsis102203142',  # Name of the package
    version='0.1',           # Version of the package
    packages=find_packages(),  # Automatically find the Python packages
    install_requires=[],     # List of dependencies (leave empty if none)
    description='A package for TOPSIS analysis.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',  # Your name
    author_email='your.email@example.com',  # Your email
    url='https://github.com/yourusername/Topsis102203142',  # URL of your project (GitHub)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
