#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
from os import environ
import json
import re
try:
    import paramiko
    import ftplib
    import telnetlib3
    import asyncio
except ModuleNotFoundError:
    pass


def checksum(data):
    result = 0
    for x in data:
        result = result ^ x
    return [result]

class PowerSwitch:
    def __init__(self, dev="/dev/ttyUSB0", port=2):
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


class RemoteExecute:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connect()

class SSHExecute(RemoteExecute):
    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, port=self.port, username=self.username, password=self.password)

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        return output, error

    def transfer_file(self, local_path, remote_path):
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()


class FTPExecute(RemoteExecute):
    def connect(self):
        self.client = ftplib.FTP(self.host, self.username, self.password)
        self.client.set_pasv(True)

    def execute_command(self, command):
        self.client.sendcmd(command)

    def transfer_file(self, local_path, remote_path):
        with open(local_path, 'rb') as f:
            self.client.storbinary(f'STOR {remote_path}', f)

class TelnetExecute(RemoteExecute):
    CMD_PROMPT = "^# "

    def connect(self):
        pass

    def execute_command(self, command):
        rules = [
            ("login: ", f"{self.username}"),    # the char before "login" prompt is \x00
            ("^Password:", f"{self.password}"),
            (self.CMD_PROMPT, "exit"),
        ]

        async def main(command):
            reader, writer = await telnetlib3.open_connection(self.host, self.port)

            if not isinstance(command, list):
                command = [command]
            for cmd in command:
                rules.insert(-1, (self.CMD_PROMPT, cmd))

            for prompt, action in rules:
                while True:
                    response = await reader.read(1024)
                    if len(response) == 0:
                        return
                    print(response, end="")

                    if re.search(prompt, response, flags=re.MULTILINE):
                        writer.write(action + "\n")
                        break

        asyncio.run(main(command))


class PowerControl:
    def __init__(self, args, unknown_args):
        parser = argparse.ArgumentParser(description='Power Control')
        parser.add_argument('operation', choices=["on", "off"], help='on/off')
        parser.add_argument('--device', help='tty device to control')
        parser.add_argument('--device_port', help='power port to control')
        parser.prog = parser.prog + " " + args.target
        self_args = parser.parse_args(unknown_args)

        args.device = self_args.device if self_args.device else args.device
        args.device_port = self_args.device_port if self_args.device_port else args.device_port

        self.power = PowerSwitch(dev=args.device, port=int(args.device_port))
        if not getattr(args, 'host', None):
            self.remote = None
        else:
            self.remote = SSHExecute(args.host, args.port, args.username, args.password)
        self.opcode = self_args.operation
        self.target = args.target

    def execute(self):
        filename = os.path.basename(__file__)
        if self.remote:
            self.remote.transfer_file(__file__, f'/tmp/{filename}')
            self.remote.execute_command(f"chmod +x /tmp/{filename}")
            self.remote.execute_command(f"/tmp/{filename} {self.target} {self.opcode} --device {self.power.dev} --device_port {self.power.port}")
        else:
            self.power.switch(self.opcode)
        

class CPControl:
    def __init__(self, args, unknown_args):
        parser = argparse.ArgumentParser(description='CP Control')
        sub_parsers = parser.add_subparsers(dest='operation', help='operation', required=True)
        run_parser = sub_parsers.add_parser('run', help='run commands')
        run_parser.add_argument('commands', nargs='+', help='commands to run')
        upgrade_parser = sub_parsers.add_parser('upgrade', help='upgrade firmware')
        upgrade_parser.add_argument('filename', help='firmware file')
        upgrade_parser.add_argument('bank', help='bank to upgrade')

        parser.prog = parser.prog + " " + args.target
        self.args = parser.parse_args(unknown_args)

        self.ftp_username = args.ftp_username
        self.ftp = FTPExecute(args.host, args.ftp_port, args.ftp_username, args.ftp_password)
        self.telnet = TelnetExecute(args.host, args.port, args.username, args.password)
        self.opcode = self.args.operation

    def execute(self):
        func = getattr(self, self.opcode)
        if not func:
            raise Exception(f"Operation {self.opcode} not found")
        func()

    def upgrade(self):
        filename = self.args.filename
        bank = self.args.bank
        basename = os.path.basename(filename)
        remote_path = f'/doc/{self.ftp_username}/{basename}'
        self.ftp.transfer_file(filename, basename)  # remote_path could not be determined by user
        self.telnet.execute_command([f"upimage {remote_path} bank{bank}", f"r{bank}"])

    def run(self):
        commands = self.args.commands
        self.telnet.execute_command('; '.join(commands))


op_map = {
    "power": PowerControl,
    "cp": CPControl
}

import sys
def main():
    print(sys.argv)
    home_path = environ.get('HOME', environ.get('HOMEPATH', '/'))
    cfg_path = os.path.join(home_path, '.remote.cfg')

    parser = argparse.ArgumentParser(description='Utils Tool')
    parser.add_argument('target', choices=["power", "cp"], help='target to perform')
    parser.add_argument('--config', default=f'{cfg_path}', help='config file')
    parser.add_argument('--host', help='Remote host')
    parser.add_argument('--port', help='Remote port')
    parser.add_argument('--username', help='Remote username')
    parser.add_argument('--password', help='Remote password')

    args, unknown_args = parser.parse_known_args()
    cfg = {}
    cls = op_map[args.target]

    try:
        with open(args.config) as f:
            config = f.read()
            json_config = json.loads(config)

            cfg: dict = json_config.get(args.target, {})
            cfg['host'] = args.host if args.host else cfg.get('host')
            cfg['port'] = args.port if args.port else cfg.get('port')
            cfg['username'] = args.username if args.username else cfg.get('username')
            cfg['password'] = args.password if args.password else cfg.get('password')
    except FileNotFoundError:
        pass

    cfg['target'] = args.target
    obj = cls(type("JsonDict", (object,), cfg), unknown_args)
    obj.execute()


if __name__ == "__main__":
    main()