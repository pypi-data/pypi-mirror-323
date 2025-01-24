from setuptools import setup, find_packages

setup(
    name='PyCypherLib',
    version='1.3.4',
    description='A Python library for secure file and string encryption using cryptography.',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='eaannist',
    author_email='eaannist@gmail.com',
    url='https://github.com/eaannist/PyCypher',
    packages=find_packages(),
    install_requires=['cryptography>=3.0.0'],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
