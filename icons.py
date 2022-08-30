#!/usr/bin/env python3

import argparse
from typing import List

from icons_extend import get_all_file_in, icon_extend, icons_extend, row_to_list

def icons_extend_wraper(args):
    row_data = get_all_file_in(args.path, args.search)
    list_data = row_to_list(row_data)
    icons_extend(path_list=list_data, width=args.width, height=args.height, dump=args.dump, case_param=args.search, path=args.path)


def icon_extend_wraper(args):
    icon_extend(args.path, args.width, args.height, args.dump)

parser = argparse.ArgumentParser(prog="icons", description="Some tools for work with icons...")
parser.add_argument(
    "path", help="Path to dir with files")
parser.add_argument(
    "-s", "--search", dest='search', type=str, choices=['deep', 'dir', 'file', 'test'], help="File search option: deep [deep] or superficial [dir]. By default it is [dir]")

subparsers = parser.add_subparsers(title='subcommands')

extend_icon_size_parser = subparsers.add_parser(
    'extend', help='Expanding the size with the preservation of the image position')
extend_icon_size_parser.add_argument(
    '-he', '--height', dest='height', type=int, help='Icon size in height')
extend_icon_size_parser.add_argument(
    '-wi', '--width', dest='width', type=int, help='Icon size in width')
extend_icon_size_parser.add_argument(
    '-d', '--dump', dest='dump', type=str, help='Path to save the result')
extend_icon_size_parser.set_defaults(func=icons_extend_wraper)


if __name__ == '__main__':
    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
