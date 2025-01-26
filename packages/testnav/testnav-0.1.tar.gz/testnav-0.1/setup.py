from setuptools import setup, find_packages

with open("README.md",'r') as f:
    description = f.read()

setup(
    name='testnav',
    version='0.1',
    packages=find_packages(),
    install_requires=[
       #dependecies are not here. 
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)