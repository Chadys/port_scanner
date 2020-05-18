import argparse
import re

import pytest

from port_scanner.args_validators import SimplerFileType, host_target, TargetArgumentParser


def test_no_support_special_file():
    with pytest.raises(argparse.ArgumentTypeError):
        SimplerFileType('r')('-')

def test_correct_ipv4():
    host_target('192.0.2.1')

def test_correct_ipv6():
    host_target('2001:DB8::1')

def test_correct_ipv4_cidr():
    host_target('192.0.2.1/24')

def test_correct_ipv6_cidr():
    host_target('2001:DB8::1/16')

def test_correct_hostname():
    host_target('test.hostname-02.com')

def test_incorrect_target():
    with pytest.raises(argparse.ArgumentTypeError):
        host_target('-incorrect')

def test_correct_one_argument():
    parser = TargetArgumentParser()
    args = parser.parse_args(['2001:DB8::1'])
    assert not args.fast
    assert args.targets_file is None
    assert args.targets == ['2001:DB8::1']

def test_correct_several_arguments():
    parser = TargetArgumentParser()
    args = parser.parse_args(['2001:DB8::1', '192.0.2.1', '192.0.2.1/24', 'test.hostname-02.com', '--fast'])
    assert args.fast
    assert args.targets_file is None
    assert args.targets == ['2001:DB8::1', '192.0.2.1', '192.0.2.1/24', 'test.hostname-02.com']

def test_correct_file_argument(mocker):
    mocker.patch('builtins.open')
    parser = TargetArgumentParser()
    args = parser.parse_args(['-targets-file', 'dummy-file.txt'])
    assert not args.fast
    assert args.targets_file
    assert not args.targets

def test_incorrect_no_argument(mocker):
    m = mocker.patch.object(TargetArgumentParser, 'error')
    parser = TargetArgumentParser()
    parser.parse_args([])
    m.assert_called_once()
    assert re.match(r'^one of the arguments .+ is required$', m.call_args[0][0])

def test_incorrect_bad_argument(mocker):
    m = mocker.patch.object(TargetArgumentParser, 'error')
    parser = TargetArgumentParser()
    parser.parse_args(['-incorrect'])
    m.assert_any_call('unrecognized arguments: -incorrect')

def test_incorrect_both_argument(mocker):
    mocker.patch('builtins.open')
    m = mocker.patch.object(TargetArgumentParser, 'error', side_effect=ValueError)
    parser = TargetArgumentParser()
    with pytest.raises(ValueError):
        parser.parse_args(['test.hostname-02.com', '-targets-file', 'dummy-file.txt'])
    m.assert_any_call('argument -targets-file: not allowed with argument targets')