from setuptools import setup, find_packages

setup(
    name="Metdley",
    version="0.1.2-2",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="Metdley",
    author_email="contact@metdley.com",
    description="A Python client for the Metdley API",
    url="https://metdley.com",
)
