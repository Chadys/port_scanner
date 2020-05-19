from __future__ import unicode_literals
from __future__ import print_function

import argparse
import ipaddress

import validators


class SimplerFileType(argparse.FileType):
    """
    Override of argpare's factory for creating file object types
    to prevent '-' value from being treated differently
    """

    def __call__(self, filename):
        # just do the same thing as parent class, without '-' special case
        try:
            try:
                with open(
                    filename, self._mode, self._bufsize, self._encoding, self._errors
                ):
                    pass
                return filename
            except AttributeError:  # take care of Python 2
                with open(filename, self._mode, self._bufsize):
                    pass
                return filename
        except (OSError, IOError) as e:
            from gettext import gettext as _

            message = _("can't open '%s': %s")
            raise argparse.ArgumentTypeError(message % (filename, e))


def host_target_type(arg_value):
    """
    Check that given value can actually be a valid hostname, ipv4, ipv6 or cidr notation
    """
    try:
        ipaddress.ip_address(arg_value)
        return arg_value
    except ValueError:
        pass
    # alternative:
    # if validators.ip_address.ipv4(arg_value) or validators.ip_address.ipv6(arg_value):
    #     return arg_value
    try:
        ipaddress.ip_network(arg_value, strict=False)
        return arg_value
    except ValueError:
        pass
    if not validators.domain(arg_value):
        raise argparse.ArgumentTypeError(
            "%s is not a hostname, ipv4, ipv6 or cidr notation" % arg_value
        )
    return arg_value


class TargetArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super(TargetArgumentParser, self).__init__(
            description="Port detection targets."
        )
        self.add_argument(
            "--fast",
            type=bool,
            nargs="?",
            default=False,
            const=True,
            help="Enable faster scan but with fewer information collected",
        )
        group = self.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "targets",
            type=host_target_type,
            nargs="*",
            default=[],
            help="one or more hostname / ipv4 / ipv6 / cidr",
        )
        group.add_argument(
            "-targets-file",
            type=SimplerFileType("r"),
            nargs="?",
            help="file containing list of hostname / ipv4 / ipv6 / cidr",
        )
