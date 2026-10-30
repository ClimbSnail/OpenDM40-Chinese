#!/usr/bin/env python3
"""Send a debug command to the meter over USBTMC (PyVISA, Windows).

    python dm.py 'DBG:KEY 0' 'DBG:TAP 100,200'
    python dm.py --query 'DBG:BOOT?'
"""

import sys

import pyvisa


def main():
    argv = sys.argv[1:]
    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r]
    if not names:
        sys.exit("meter not found over USBTMC")
    d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=15000)

    i = 0
    while i < len(argv):
        if argv[i] == "--query":
            print(d.query(argv[i + 1]).strip())
            i += 2
        else:
            d.write(argv[i])
            print("sent: %s" % argv[i])
            i += 1
    d.close()


main()
