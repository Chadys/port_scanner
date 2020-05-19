from __future__ import unicode_literals
from __future__ import print_function

import re

import pytest

from port_scanner import PortScanner


def test_several_targets():
    targets = ["test.hostname-02.com", "192.0.2.1/24"]
    ps = PortScanner(targets=targets)
    assert ps.command[-2:] == targets


def test_file_targets():
    targets_file = "dummy-file.txt"
    ps = PortScanner(targets=[], targets_file=targets_file)
    assert ps.command[-1] == targets_file
    assert ps.command[-2] == PortScanner._file_option


def test_fast_option():
    targets_file = "dummy-file.txt"
    ps1 = PortScanner(targets=[], targets_file=targets_file, fast=False)
    ps2 = PortScanner(targets=[], targets_file=targets_file, fast=True)
    assert ps1.command != ps2.command


def test_no_target():
    with pytest.raises(ValueError) as e:
        PortScanner(targets=[])
    assert re.match(r"^.+ instance needs at least one target$", str(e.value))
