#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Example: python remote_execute.py power_switch.py --config config.json -- on
import paramiko
import argparse
import os
from os import environ
import json

class RemoteExecute:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connect()

    def execute(self, command, args):
        self.filename = command
        print(f"Executing command: {command} on {self.host}:{self.port} with {self.username}/{self.password}")
        self.transfer_file(self.filename, f'/tmp/{self.filename}')
        self.execute_command(f"chmod +x /tmp/{self.filename}")
        self.execute_command(f"/tmp/{self.filename} {' '.join(args)}")
        

class SSHExecute(RemoteExecute):
    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, port=self.port, username=self.username, password=self.password)

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error: {error}")
        return output, error

    def transfer_file(self, local_path, remote_path):
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()


def main():
    home_path = environ.get('HOME', environ.get('HOMEPATH', '/'))
    cfg_path = os.path.join(home_path, '.remote.cfg')

    parser = argparse.ArgumentParser(description='Remote Execute Tool')
    parser.add_argument('file', help='file to be executed')
    parser.add_argument('--config', action='store_true', default=f'{cfg_path}', help='config file')
    parser.add_argument('--host', action='store_true', default='localhost', help='Remote host')
    parser.add_argument('--port', action='store_true', default=22, help='Remote port')
    parser.add_argument('--username', action='store_true', default='root', help='Remote username')
    parser.add_argument('--password', action='store_true', default='password', help='Remote password')

    args, remaining_args = parser.parse_known_args()

    try:
        with open(args.config) as f:
            config = f.read()
            json_config = json.loads(config)
            json_config = json_config.get('cp', {})
            args.host = json_config.get('host', args.host)
            args.port = json_config.get('port', args.port)
            args.username = json_config.get('username', args.username)
            args.password = json_config.get('password', args.password)
    except FileNotFoundError:
        pass

    remote = SSHExecute(args.host, args.port, args.username, args.password)
    remote.execute(args.file, remaining_args)


if __name__ == "__main__":
    main()