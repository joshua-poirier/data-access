from setuptools import setup, find_packages

setup(
    name="data-access",
    packages=find_packages(exclude=["tests", "tests.*"]),
    zip_safe=False,
    author="Joshua Poirier",
    description="Tools to access data",
    url="https://github.com/joshua-poirier/data-access",
)
