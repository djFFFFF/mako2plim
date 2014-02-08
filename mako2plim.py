# coding: utf-8

from argparse import ArgumentParser
from converter import Converter

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--file', help='target mako file to be translated')
    args = parser.parse_args()
    file = args.file
    converter = Converter(file)
    converter.convert()

if __name__ == '__main__':
    main()
