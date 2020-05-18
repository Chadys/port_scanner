from port_scanner import PortScanner
from port_scanner.args_validators import TargetArgumentParser

if __name__ == "__main__":
    parser = TargetArgumentParser()
    args = parser.parse_args()
    ps = PortScanner(**vars(args))
    ps()
