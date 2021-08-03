from __future__ import print_function
from __future__ import unicode_literals

import errno
import os
import subprocess
import sys


class PortScanner:
    xml_output_file_name = "tmp_scan.xml"
    _deep_scan_options = [
        "-sSU",
        "-pT:-,U:631,161,137,123,138,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69",
    ]
    _fast_scan_options = ["-sS", "-F"]
    _other_options = [
        "-A",  # version detection, NSE with the default set of scripts, remote OS detection, and traceroute
        "--osscan-limit",  # only try OS detection on promising target
        "--min-hostgroup",  # perf related option
        "256",
        "-T",  # perf related option
        "aggressive",
        "--resolve-all",  # scan all IP address if more than one correspond to given hostname
        "-PE",  # rule to detect online host
        "-PP",  # rule to detect online host
        "-PS80,443",  # rule to detect online host
        "-PA3389",  # rule to detect online host
        "-PU40125",  # rule to detect online host
        "--script",  # extra NSE script
        # infortunatelly `nmap --script-updatedb` doesn't work with subfolder,
        # or else this wouldn't have been needed since both scripts have 'default' category
        "vulscan,nmap-vulners",
        "-v",  # verbose
    ]
    _output_options = ["-oX", xml_output_file_name]
    _file_option = "-iL"
    _executable_name = "nmap"
    _html_executable_name = "xsltproc"
    _html_generate_command = [
        _html_executable_name,
        xml_output_file_name,
        "-o",
        "scan.html",
    ]

    def __init__(self, targets, targets_file=None, fast=False, debug=False):
        scan_option = self._fast_scan_options if fast else self._deep_scan_options
        if debug:
            scan_option.append("-d")
        # self.command = [self._executable_name, *scan_option, *self._other_options, *self._output_options]
        # Python 2.7 compatible code instead
        self.command = (
            [self._executable_name]
            + scan_option
            + self._other_options
            + self._output_options
        )
        if targets_file is not None:
            self.command.extend([self._file_option, targets_file])
            return
        if targets:
            self.command.extend(targets)
            return
        raise ValueError(
            "%s instance needs at least one target" % self.__class__.__name__
        )

    @staticmethod
    def react_to_executable_not_found(exception_file_name, exe_name):
        if exception_file_name == exe_name:
            print(
                "%s wasn't found on your system, did you correctly install it?"
                % exe_name,
                file=sys.stderr,
            )
            exit(errno.ENOENT)

    def __call__(self, *args, **kwargs):
        try:
            # never put shell=True with unsanitized user input for security reason
            subprocess.check_call(self.command, shell=False)
        except subprocess.CalledProcessError as e:
            exit(e.returncode)
        except EnvironmentError as e:  # can't use FileNotFoundError because of Python 2.7 compatibility
            self.react_to_executable_not_found(e.filename, self._executable_name)
            raise e
        self.produce_html()

    def produce_html(self):
        try:
            # never put shell=True with unsanitized user input for security reason
            subprocess.check_call(self._html_generate_command, shell=False)
        except subprocess.CalledProcessError as e:
            exit(e.returncode)
        except EnvironmentError as e:  # can't use FileNotFoundError because of Python 2.7 compatibility
            self.react_to_executable_not_found(e.filename, self._html_executable_name)
            raise e
        try:
            os.remove(self.xml_output_file_name)
        except OSError:
            print("Can't delete %s temporary file" % self.xml_output_file_name)
