#!/usr/bin/python
# -*- coding: UTF-8 -*-
import paramiko
import socket
import select


class SSH:
    def __init__(self, ip, port, user, password, log):
        if ip.startswith('127.') or ip == 'localhost':
            raise
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.ssh = None
        self.stdin = None
        self.stderr = None
        self.stdout = None
        self.log = log
        self.conn()

    def conn(self):
        try:
            self.ssh = paramiko.client.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, username=self.user,
                             password=self.password)

        except Exception as e:
            print(e.__str__())
            self.log.info(e.__str__())
            self.ssh = None

    def run(self, cmd):
        if self.ssh:
            self.log.info(f"开始执行命令：{cmd}")
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.stdin = stdin
            self.stderr = stderr
            self.stdout = stdout
            out = []
            for line in stdout.readlines():
                out.append(line)
            return out

    def run_pty(self, cmd):
        self.log.info(f"开始执行命令：{cmd}")
        # func = getattr(self.ssh, 'exec_command')
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True)
        self.stdout = stdout
        out = []
        stdout._set_mode("b")
        for line in stdout.xreadlines():
            line = line.decode()
            out.append(line)
        return out

def open_sock(source_ip, source_port, wait):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setblocking(0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception as e:
        return False, e.__str__()
    if source_port:
        sock.bind((source_ip, source_port))
    sock.settimeout(wait)
    return True, sock

def listen_sock(sock):
    while True:
        inputready, outputready, exceptready = select.select([sock], [], [], 1)
        for s in inputready:
            if s == sock:
                buf = None
                buf = sock.recvfrom(0xffff)
                rcv = buf[0].decode()
                print(rcv)
                yield rcv

