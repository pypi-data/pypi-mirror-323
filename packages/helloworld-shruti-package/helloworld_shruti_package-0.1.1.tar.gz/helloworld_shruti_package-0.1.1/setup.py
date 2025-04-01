from setuptools import setup, find_packages

setup(
    name="helloworld_shruti_package",
    version="0.1.1",
    packages=find_packages(),
    description="A package to print Hello World",
    author="Your Name",
    author_email="your.email@example.com",
    include_package_data=True,
    zip_safe=False,
)
