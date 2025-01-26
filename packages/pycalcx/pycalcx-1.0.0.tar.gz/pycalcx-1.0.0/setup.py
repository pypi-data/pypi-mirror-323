from setuptools import setup, find_packages

setup(
    name='pycalcx',
    version='1.0.0',
    author='Ch. Abdul Wahab',
    author_email='ch.abdul.wahab310@gmail.com',
    description='A simple calculator library for basic mathematical operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/calc_toolkit',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
