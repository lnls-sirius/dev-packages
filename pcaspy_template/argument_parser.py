
import argparse


def get_argument_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('name', help='soft IOC name')
    parser.add_argument('-d', '--dest',
            help='destination directory (default: .)')
    
    return parser
