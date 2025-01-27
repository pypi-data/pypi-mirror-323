from setuptools import setup, find_packages


with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="cartesi",
    version="0.1.1",
    description="A Python Framework for Cartesi Distributed Applications",
    author="Grael",
    keywords=["crypto", "DApps" , "Decentralized Application"],
    license="Apache License",
    packages=find_packages(),
    install_requires=[
        "requests >= 2.31.0",
        "pydantic < 2",
        "pytest ~= 7.4.0",
        "eth-abi ~= 4.2.1",
        "pycryptodome ~= 3.19.0",
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
