#!/usr/bin/env python3
import server
import sys


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    else:
        prefix = ''

server.run(prefix)
