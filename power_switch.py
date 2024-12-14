#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

def checksum(data):
    result = 0
    for x in data:
        result = result ^ x
    return [result]

class PowerSwitch:
    def __init__(self, dev="/dev/ttyUSB0", port=0x02):
        self.power_status = False
        self.dev = dev
        self.port = port

    def ON(self):
        return [0xa0, self.port, 0x01]

    def OFF(self):
        return [0xa0, self.port, 0x00]

    def switch(self, op: str):
        op = getattr(self, op.upper())
        seq = op() + checksum(op())
        with open(self.dev, 'wb') as f:
            f.write(bytes(seq))
            f.flush()


def main():
    parser = argparse.ArgumentParser(description='Power Switch Tool')
    parser.add_argument('operation', choices=['on', 'off'], help='Operation to perform')
    parser.add_argument('--dev', action='store_true', default='/dev/ttyUSB0', help='Uart device')
    parser.add_argument('--port', action='store_true', default=2, help='Power port')

    args = parser.parse_args()

    power = PowerSwitch(dev=args.dev, port=args.port)
    power.switch(args.operation)

if __name__ == "__main__":
    main()