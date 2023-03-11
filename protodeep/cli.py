from rich_argparse import RichHelpFormatter

import argparse
from typing import *
import sys


def parse_and_run():
    RichHelpFormatter.styles["argparse.groups"] = "light_goldenrod2"
    RichHelpFormatter.styles["argparse.metavar"] = "light_cyan1"
    RichHelpFormatter.styles["argparse.args"] = "deep_sky_blue1"

    parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)

    parser.add_argument("proto_file", nargs='?')
    parser.add_argument('-t', '--type', required=True, type=str, help="Either protobuf (raw protobuf content), or protodeep (a ProtoDeep file).")
    parser.add_argument('-d', '--definitions', type=str, help="The file containing the custom protobuf definitions.")
    parser.add_argument('-na', '--no-autodetect', action='store_true', default=False, help="Don't try to autodetect if it's a raw HTTP request.")
    parser.add_argument('-s', '--stdin', action='store_true', default=False, help="Parse from stdin.")
    parser.add_argument('-b', '--base64', action='store_true', default=False, help="If this is a base64 input, so it automatically decodes it.")
    parser.add_argument('-bi', '--bruteforce-index', type=int, default=20, help="The index up to which to try bruteforce to find Protobuf content. Default : 20", metavar="NUMBER")
    parser.add_argument('-he', '--hide-empty', action='store_true', default=False, help="Hide the empty values.")
    parser.add_argument('-np', '--no-print', action='store_true', default=False, help="Don't print the decoded protobuf.")
    parser.add_argument('-m', '--match', type=str, default=[], action='append', help="Match anything with the given string. You can use '?' and '*' to wildcard match.Ex : \"*token*\"", metavar="MASK")
    parser.add_argument('-mk', '--match-keychain', type=str, default=[], action='append', help="Match keychains with the given string.", metavar="MASK")
    parser.add_argument('-mv', '--match-value', type=str, default=[], action='append', help="Match values with the given string.", metavar="MASK")
    parser.add_argument('-f', '--filter', type=str, default=[], action='append', help="Filter anything with the given string. You can use '?' and '*' to wildcard match.", metavar="MASK")
    parser.add_argument('-fk', '--filter-keychain', type=str, default=[], action='append', help="Filter keychains with the given string.", metavar="MASK")
    parser.add_argument('-fv', '--filter-value', type=str, default=[], action='append', help="Filter values with the given string.", metavar="MASK")
    parser.add_argument('-epf', '--export-protofile', nargs='?', const='default.proto', type=str, help="Export the proto file with the definitions.", metavar="PROTOFILE_FILENAME")
    parser.add_argument('-epd', '--export-protodeep', nargs='?', const='default.pdeep', type=str, help="Export a protodeep file, to reuse in ProtoDeep.", metavar="PROTODEEP_FILENAME")
    parser.add_argument('-c', '--compile', nargs='?', const='default_pb2.py', type=str, help="Compile protobuf into a Python file.", metavar="PYTHON_FILENAME")
    parser.add_argument('-n', '--name', type=str, default="Schema", help="Name of the schema when exporting into a proto file.", metavar="SCHEMA_NAME")

    ### Parsing
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    process_args(args)

def process_args(args: argparse.Namespace):
    from protodeep import analyze
    analyze(
        proto_file=args.proto_file,
        defs_file=args.definitions,
        export_protobuf=args.export_protofile,
        export_protodeep=args.export_protodeep,
        hide_empty=args.hide_empty,
        match_any=args.match,
        match_keychain=args.match_keychain,
        match_value=args.match_value,
        filter_any=args.filter,
        filter_keychain=args.filter_keychain,
        filter_value=args.filter_value,
        bruteforce_index=args.bruteforce_index,
        stdin=args.stdin,
        no_autodetect=args.no_autodetect,
        base64_input=args.base64,
        data_type=args.type,
        compile=args.compile,
        no_print=args.no_print,
        schema_name=args.name
    )