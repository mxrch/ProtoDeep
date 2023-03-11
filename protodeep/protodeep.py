import sys


def main():
    version = sys.version_info
    if (version < (3, 10)):
        print('[-] ProtoDeep only works with Python 3.10+.')
        print(f'Your current Python version : {version.major}.{version.minor}.{version.micro}')
        sys.exit(1)

    from protodeep.cli import parse_and_run

    parse_and_run()