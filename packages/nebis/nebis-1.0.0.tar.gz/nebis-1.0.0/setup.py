from setuptools import setup, find_packages

setup(
    name="nebis",
    version="1.0.0",
    author="NebisDB",
    author_email="nebisdb@gmail.com",
    description="Nebis Python client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nebis-db/pynebis",
    packages=find_packages(),
    install_requires=[
        "requests",
        "urllib3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
