from __future__ import unicode_literals

from port_scanner.args_validators import TargetArgumentParser

if __name__ == "__main__":
    parser = TargetArgumentParser()
    args = parser.parse_args()
