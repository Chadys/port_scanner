# Port Scanner

This tool allow you to simply scan ports from a list of network targets and to get back an HTML report.
Internally it uses `nmap` and make opinionated decisions about what options should be used for a broad usage.
Choices were made to keep balance between speed and relevance of results.
For a more specialised scan port, you'll need to run `nmap` yourself with different options, 
the goal of this tool is NOT to be a complete wrapper.

## Installation
For now this package is not available through `pip`, 
you'll need to clone it and to install it locally with `pip install .`.

## Dependencies
You must have [`nmap`](https://nmap.org/book/install.html) (obviously) and [`xsltproc`](http://www.xmlsoft.org/XSLT/xsltproc.html) (for HTML generation) installed on your machine.
Then you'll need to execute the following two commands:
```shell script
git clone https://github.com/vulnersCom/nmap-vulners <nmap_installation_folder>/scripts/nmap-vulners
git clone https://github.com/scipag/vulscan <nmap_installation_folder>/scripts/vulscan
```
These scripts are used to improve the CVE detection capacities of `nmap`.

## Python version
This tool is compatible with Python 2.7+

## Usage
This module can be used like an executable script from command line like so:
```shell script
sudo python -um port_scanner (-targets-file [TARGETS_FILE] | targets [targets ...]) [--fast]
```
- `targets` must be one or several hostname, ipv4, ipv6 or cidr
- `TARGETS_FILE` must be a valid path to a file containing a list of hostname, ip or cidr
- `targets` and `TARGETS_FILE` are mutually exclusive.
- `--fast` make the scan quicker but less thorough.
- `sudo` is needed to give `nmap` low-level packet control

Instead, you can also launch the scan yourself (but you'll still need `sudo` to execute the python script):
```python
from port_scanner import PortScanner

PortScanner(targets=["scanme.nmap.org"], fast=False)()
```
Notice the parentheses at the end.
Don't forget to check for validity of targets argument if you get them from untrusted source; 
`port_scanner.args_validators.host_target_type` can be used to validate the items in `targets`.

## Results
Using the CLI or the `PortScanner` object directly, this tool will produce one file in your current directory: "scan.html".
You can open this file in your favorite browser.
If you get a "tmp_scan.xml" and no "scan.html", that probably means that you didn't install `xsltproc`, check your error messages.
To retry the HTML file generation without redoing the whole scan, you can use this code (no need for `sudo` this time):
```python
from port_scanner import PortScanner

# don't worry about the args here, just give it valid ones
PortScanner(targets=["scanme.nmap.org"], fast=False).produce_html()
```
If you get BOTH a "tmp_scan.xml" and a "scan.html" files, you did some weird things and I can't help you.
You can just delete the XML one if you don't want it.

## Tests
For that you'll need to install this package's registered tests dependencies.
To launch full tests in environment with packaging, you can use [`tox`](https://tox.readthedocs.io/en/latest/) 
(for now the py27 env is failing because of some problem caused by `ipaddress` installation, it should be adressed soon).
Or you can just run the tests directly in your environment: `python -m pytest` 
(the `-m` shouldn't be necessary once you have [installed the package](https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code)).

