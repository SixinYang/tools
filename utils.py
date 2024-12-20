#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
from os import environ
import json
import re
import subprocess
import atexit
from copy import deepcopy

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

class Cache:
    def __init__(self, fname):
        self.data = {}
        self.fname = fname
        atexit.register(self.exit_handler)

        if os.path.isfile(fname):
            with open(fname) as f:
                self.data = json.load(f)

    def exit_handler(self):
        with open(self.fname, 'w') as f:
            json.dump(self.data, f)

    @staticmethod
    def cacheit(keys):
        def decorator(func):
            def wrapper(this, *args, **kwargs):
                global gcache
                if isinstance(keys, list):  # get from self attributes
                    key = '.'.join([getattr(this, k) for k in keys])
                elif isinstance(keys, tuple):  # get from positional arguments
                    key = '.'.join([args[k] for k in keys])

                if key in gcache.data:
                    print(f"Cache hit for {key}")
                    return gcache.data[key]
                
                result = func(this, *args, **kwargs)
                gcache.data[key] = deepcopy(result)
                return result
            return wrapper
        return decorator

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
            result = ""
            reader, writer = await telnetlib3.open_connection(self.host, self.port)

            if not isinstance(command, list):
                command = [command]
            for cmd in command:
                rules.insert(-1, (self.CMD_PROMPT, cmd))

            for prompt, action in rules:
                while True:
                    response = await reader.read(1024)
                    if len(response) == 0:
                        return result
                    print(response, end="")
                    result += response

                    if re.search(prompt, response, flags=re.MULTILINE):
                        writer.write(action + "\n")
                        break
            return result

        return asyncio.run(main(command))

class LocalShell:
    def execute_command(self, command):
        return subprocess.run(command, shell=True, text=True, capture_output=True)


class Base:
    def __init__(self, cfg, op, args, gconfig):
        self.cfg = cfg  # json format
        self.op = op    # string format
        self.args = args    # object format
        self.gconfig = gconfig  # json format
        self.init()

class Power(Base):
    def init(self):
        if not self.cfg:
            self.cfg = {
                "device": self.args.device,
                "device_port": self.args.device_port,
            }

        self.power = PowerSwitch(dev=self.cfg["device"], port=int(self.cfg["device_port"]))
        if not self.cfg.get("host", None):
            self.remote = None
        else:
            self.remote = SSHExecute(self.cfg["host"], self.cfg["port"], self.cfg["username"], self.cfg["password"])

    def execute(self):
        filename = os.path.basename(__file__)
        if self.remote:
            self.remote.transfer_file(__file__, f'/tmp/{filename}')
            self.remote.execute_command(f"chmod +x /tmp/{filename}")
            self.remote.execute_command(f"/tmp/{filename} {self.__class__.__name__.lower()} --device {self.power.dev} --device_port {self.power.port} {self.op}")
        else:
            self.power.switch(self.op)
        

class Cp(Base):
    cmds = {
        "setup_debug": "export LD_LIBRARY_PATH=/doc/OPERATOR:$LD_LIBRARY_PATH; export PATH=$PATH:/doc/OPERATOR; qconn",
        "check_files": "ls /doc/OPERATOR|xargs",
        "kill_prog": "pm -u {pname}; pm -k {pname}",
        "run_prog": "pm -u {pname}; pm -k {pname}; export LD_LIBRARY_PATH=/doc/OPERATOR:$LD_LIBRARY_PATH; chmod a+rx /doc/OPERATOR/{target}; /doc/OPERATOR/{target} {args}",
        "get_info": '''PID=$(pm -P|grep ###|cut -d\  -f2); NAME=$(ps -o pid,cmd|grep $PID|awk '{print $2}'); ARGS=$(ps -o pid,args|grep $PID|grep -v grep|awk '{$1=""; $2=""; print}'); echo ### $PID $NAME $ARGS'''
    }

    pname_info = {
        "poller-1m": ["aonPollerPro", "-a POLLER_FLASH_1 -n CIRCUIT_PACK.1.SYSTEM_INFORMATION.1.APPLICATION_INFORMATION.1 -n CIRCUIT_PACK.1.SYSTEM_INFORMATION.1.APPLICATION_INFORMATION.2 -n CIRCUIT_PACK.1.SYSTEM_INFORMATION.1.FILE_SYSTEM_INFORMATION.1 -w GateSystemInfoReady -p CIRCUIT_PACK.1.SOFTWARE_UPGRADE_LOAD.1 -i priorityOperationInProgress -s"]
    }

    def init(self):
        self.ftp = FTPExecute(self.cfg["host"], self.cfg["ftp_port"], self.cfg["ftp_username"], self.cfg["ftp_password"])
        self.telnet = TelnetExecute(self.cfg["host"], self.cfg["telnet_port"], self.cfg["telnet_username"], self.cfg["telnet_password"])

    def execute(self):
        func = getattr(self, self.op)
        if not func:
            raise Exception(f"Operation {self.op} not found")
        func()

    def upgrade(self):
        filename = self.args.filename
        bank = self.args.bank
        basename = os.path.basename(filename)
        remote_path = f'/doc/{self.cfg["ftp_username"]}/{basename}'
        self.ftp.transfer_file(filename, basename)  # remote_path could not be determined by user
        self.telnet.execute_command([f"upimage {remote_path} bank{bank}", f"r{bank}"])

    def run(self):
        commands = self.args.commands
        self.telnet.execute_command('; '.join(commands))

    def setup_debug(self):
        self.telnet.execute_command(self.cmds['setup_debug'])

    def debug(self):
        pname = self.args.pname
        info = self._get_process_info(pname)
        if info:
            pid, name, args = info
        else:
            print(f"Process {pname} not found")
            pid, name, args = None, *self.pname_info.get(pname, [None, None])
            if not name:
                print(f"information for {pname} not found")
                return
        self._upload_files(name)
        self.telnet.execute_command(self.cmds['run_prog'].format(pname=pname, target=name, args=args))

    @Cache.cacheit((0,))
    def _get_process_info(self, pname):
        response = self.telnet.execute_command(self.cmds['get_info'].replace('###', pname))
        cmd = re.findall(r'^{pname} ([^ ]+) ([^ ]+) (.*)'.format(pname=pname), response, re.MULTILINE)
        if cmd:
            cmd = list(cmd[0])
            cmd[-1] = cmd[-1].strip()
            return cmd

    def _upload_files(self, program):
        build = Build(self.gconfig["build"], "dep", json2obj({"program": program}), self.gconfig)
        files = build.dep()
        files.append(build.program_path)
        cmds = []

        # upload is too slow sometimes, so check if the file is already there
        exist_files = self.telnet.execute_command(self.cmds['check_files'])
        files = [file for file in files if os.path.basename(file) not in exist_files]
        for file in files:
            self.ftp.transfer_file(file, f'{os.path.basename(file)}')


class Build(Base):
    cmds = {
        "find_libs": "make -j16 -C {root} DEBUG=1 JDSU_PRODUCT={product} TOOLCHAIN={toolchain} src.files | grep {program} | cut -d\) -f1|cut -d\( -f2",
    }

    def init(self):
        self.root = self.cfg.get("root", None)
        self.product = self.cfg.get("product", None)
        self.toolchain = self.cfg.get("toolchain", None)
        self.program = self.args.program
        self.shell = LocalShell()

    def execute(self):
        func = getattr(self, self.op)
        if not func:
            raise Exception(f"Operation {self.opcode} not found")
        return func()

    @Cache.cacheit(["product", "toolchain", "program"])
    def dep(self):
        if not self.root:
            raise Exception("Root path not found")
        result = self.shell.execute_command(self.cmds['find_libs'].format(root=self.root,
            product=self.product, toolchain=self.toolchain, program=self.program))
        libs = result.stdout.split()
        libs = ["{root}/build/{product}/{toolchain}/rootfs/opt/lumentum/lib/{lib}.1".format(root=self.root, product=self.product, toolchain=self.toolchain, lib=lib) for lib in libs]
        return libs

    @property
    def program_path(self):
        return "{root}/build/{product}/{toolchain}/rootfs/opt/lumentum/bin/{program}".format(
            root=self.root, product=self.product, toolchain=self.toolchain, program=self.program)

def_args = {
    "power": {
        "on": None,
        "off" : None,
        "--device": None,
        "--device_port": None,
    },
    "cp": {
        "run": ("commands",),   # use tuple to indicate multiple arguments
        "upgrade": ["filename", "bank"],
        "debug": ["pname"]
    },
    "build": {
        "dep": ["program"]
    },
}

def add_parser(parser, name, cfg):
    sub_parsers = None

    for k, v in cfg.items():
        if k.startswith("--"):
            parser.add_argument(k)
            continue

        if not sub_parsers:
            sub_parsers = parser.add_subparsers(required=True, dest=f'{name}_op', help='target')
        sub_parser = sub_parsers.add_parser(k)

        if isinstance(v, dict):
            add_parser(sub_parser, k, v)
        elif isinstance(v, tuple):
            for arg in v:
                sub_parser.add_argument(arg, nargs='+')
        elif isinstance(v, list):
            for arg in v:
                sub_parser.add_argument(arg)


def json2obj(d):
    return type("JsonDict", (object,), d)


gcache = None
def main():
    home_path = environ.get('HOME', environ.get('HOMEPATH', '/'))
    cfg_path = os.path.join(home_path, '.vi.cfg')
    cache_path = os.path.join(home_path, '.vi.cache')

    parser = argparse.ArgumentParser(description='Utils Tool')
    parser.add_argument('--config', default=f'{cfg_path}', help='config file')
    parser.add_argument('--cache', default=f'{cache_path}', help='cache file')
    add_parser(parser, "root", def_args)
    args = parser.parse_args()

    global gcache
    gcache = Cache(args.cache)

    try:
        with open(args.config) as f:
            json_config = json.load(f)
    except Exception:
        json_config = {}

    cls = globals()[args.root_op.capitalize()]
    obj = cls(json_config.get(args.root_op), getattr(args, f'{args.root_op}_op'), args, json_config)
    ret = obj.execute()
    print(ret)


if __name__ == "__main__":
    main()