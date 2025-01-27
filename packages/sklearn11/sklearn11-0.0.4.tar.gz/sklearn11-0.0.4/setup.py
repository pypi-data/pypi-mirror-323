from setuptools import setup, find_packages

setup(
    name="sklearn11",
    version="0.0.4",
    author="olcay",
    author_email="olcay.aydn25@gmail.com",
    description="100 alcaz",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ozbere31/sklearn11",
    packages=find_packages(),
    include_package_data=True,  # Bu satırı ekleyin
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)