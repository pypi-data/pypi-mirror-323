from setuptools import setup, find_packages

setup(
    name='get_sc_log',
    version='0.0.8',
    description='查询日记',
    author='river',
    packages=find_packages(),
    install_requires=[
    "requests>=2.0.0",
    "jsonpath>=0.82",
             ],
)
