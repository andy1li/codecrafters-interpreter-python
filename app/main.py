import argparse, sys
from lox.lox import Lox

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('filename')
    args = parser.parse_args()
    
    lox = Lox(args.filename)
    match args.command:
        case 'tokenize' : lox.scan()
        case 'parse'    : lox.parse()
        case _          : sys.exit(1)

if __name__ == '__main__':
    main()
