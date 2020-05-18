import errno
import subprocess
import sys


class PortScanner:
    _deep_scan_options = [
        "-sSU",
        "-pT:-,U:631,161,137,123,138,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69",
    ]
    _fast_scan_options = ["-sS", "-F"]
    _other_options = [
        "-A",
        "--osscan-limit",
        "--min-hostgroup",
        "256",
        "-T",
        "aggressive",
        "--resolve-all",
        "-PE",
        "-PP",
        "-PS80,443",
        "-PA3389",
        "-PU40125",
    ]
    _file_option = "-iL"
    _executable_name = "nmap"

    def __init__(self, targets, targets_file=None, fast=False):
        scan_option = self._fast_scan_options if fast else self._deep_scan_options
        # self.command = [self._executable_name, *scan_option, *self._other_options]
        # Python 2.7 compatible code instead
        self.command = [self._executable_name] + scan_option + self._other_options
        if targets_file is not None:
            self.command.extend([self._file_option, targets_file])
            return
        if targets:
            self.command.extend(targets)
            return
        raise ValueError(
            "%s instance needs at least one target" % self.__class__.__name__
        )

    def __call__(self, *args, **kwargs):
        try:
            subprocess.check_call(self.command, shell=False)
        except subprocess.CalledProcessError as e:
            exit(e.returncode)
        except FileNotFoundError as e:
            if e.filename == self._executable_name:
                print(
                    "%s wasn't found on your system, did you correctly install it?"
                    % self._executable_name,
                    file=sys.stderr,
                )
                exit(errno.ENOENT)
            raise e
