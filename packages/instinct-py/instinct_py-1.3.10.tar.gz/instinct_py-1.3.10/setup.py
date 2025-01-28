""" Setup file for the Instinct Python SDK. """

from setuptools import setup, find_packages

setup(
    name="instinct_py",
    version="1.3.10",
    author="Nexstem India Private Limited",
    author_email="developers@nexstem.ai",
    description="Control and interact with your Instinct headset.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "License :: Free To Use But Restricted",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
