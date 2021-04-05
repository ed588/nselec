from setuptools import find_packages, setup
from nselec import __version__ as nselec_version

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="nselec",
    version=nselec_version,
    author="ed588",
    description="Election website for your NationStates region",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ed588/nselec",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "tinydb", "tinydb-serialization", "ago"],
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ],
)
