import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="port_scanner-CHADYS",
    version="0.0.1",
    author="Julie Rymer",
    author_email="rymerjulie.pro@gmail.com",
    description="A thin wrapper around nmap to scan port and generate a HTML report",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chadys/port_scanner",
    packages=setuptools.find_packages(".", exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=2.7",
    install_requires=["ipaddress>=1.0.23;python_version<'3.3'", "validators>=0.15.0"],
    tests_require=["pytest>=4.6.10", "pytest-mock>=2.0.0", "tox>=3.15.0"],
)
