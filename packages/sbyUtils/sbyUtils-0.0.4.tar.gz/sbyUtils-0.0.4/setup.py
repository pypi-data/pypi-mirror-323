from setuptools import setup, find_packages

setup(
    name='sbyUtils',
    version='0.0.4',
    packages=find_packages(),
    author='Shai Ben Yosef',
    description= 'Some basic utils for day to day python programming',
    long_description= open('README.md').read(),
    long_description_content_type='text/markdown'
)