import sys

from port_scanner import PortScanner
from port_scanner.args_validators import TargetArgumentParser


def convert_args_to_unicode_if_needed():
    """
    In Python 2.7, sys.argv are str and not unicode,
    ipaddress package only works on unicode,
    hence we need to decode given arguments
    """
    if sys.version_info.major == 2:
        sys.argv = map(lambda arg: arg.decode(sys.stdout.encoding), sys.argv)


if __name__ == "__main__":
    convert_args_to_unicode_if_needed()
    parser = TargetArgumentParser()
    args = parser.parse_args()
    ps = PortScanner(**vars(args))
    ps()
