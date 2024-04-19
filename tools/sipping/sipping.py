#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import time
from io import StringIO
import re
from pprint import pprint
import select
from string import Template
from .build_template.response import PlatformResponse as PLRESP
from .build_template.request import PlatformRequest as PLREQ
from utils import run_func
from tools import *

# logger, _ = log_config(filename='log', fix=True)


class CustomTemplate(Template):
    idpattern = r'[a-z][\.\-_a-z0-9]*'


class SipError(Exception):
    pass


class SipUnpackError(SipError):
    pass


class SipNeedData(SipUnpackError):
    pass


class SipPackError(SipError):
    pass


def canon_header(s):
    exception = {
        'call-id': 'Call-ID',
        'cseq': 'CSeq',
        'www-authenticate': 'WWW-Authenticate'
    }
    short = ['allow-events', 'u', 'call-id', 'i', 'contact', 'm', 'content-encoding', 'e',
        'content-length', 'l', 'content-type', 'c', 'event', 'o', 'from', 'f', 'subject', 's', 'supported', 'k', 'to', 't', 'via', 'v']
    s = s.lower()
    return ((len(s) == 1) and s in short and canon_header(short[short.index(s) - 1])) \
        or (s in exception and exception[s]) or '-'.join([x.capitalize() for x in s.split('-')])


def parse_headers(f):
        """Return dict of HTTP headers parsed from a file object."""
        d = {}
        while 1:
            line = f.readline().strip()
            if not line:
                break
            l = line.split(None, 1)
            if not l[0].endswith(':'):
                break
                # raise SipUnpackError('invalid header: %r' % line)
            k = l[0][:-1].lower()
            d[k] = len(l) != 1 and l[1] or ''
        return d


def parse_body(f, headers):
    """Return SIP body parsed from a file object, given HTTP header dict."""
    if 'content-length' in headers:
        idx = int(headers['content-length'])
        body = f.read(idx)
        if len(body) != idx:
            raise SipNeedData('short body (missing %d bytes)' % (idx - len(body)))
    elif 'content-type' in headers:
        body = f.read()
    else:
        body = ''
    return body


def parse_support_funcs():
    res = PLRESP()
    req = PLREQ()
    funcs = res.funcs
    funcs.extend(req.funcs)
    return funcs  


class Message:
    """SIP Protocol headers + body."""
    __metaclass__ = type
    __hdr_defaults__ = {}
    headers = None
    body = None

    def __init__(self, *args, **kwargs):
        if args:
            self.unpack(args[0])
        else:
            self.headers = {}
            self.body = ''
            for k, v in self.__hdr_defaults__.iteritems():
                setattr(self, k, v)
            for k, v in kwargs.iteritems():
                setattr(self, k, v)

    def unpack(self, buf):
        f = StringIO(buf)
        # Parse headers
        self.headers = parse_headers(f)
        # Parse body
        self.body = parse_body(f, self.headers)
        # Save the rest
        self.data = f.read()

    def pack_hdr(self):
        return ''.join(['%s: %s\r\n' % (canon_header(k), v) for k, v in self.headers.items()])

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return '%s\r\n%s' % (self.pack_hdr(), self.body)


class Request(Message):
        """SIP request."""
        __hdr_defaults__ = {
            'method': 'INVITE',
            'uri': 'sip:user@example.com',
            'version': '2.0',
            'headers': {'to': '', 'from': '', 'call-id': '', 'cseq': '', 'contact': ''}
        }
        __methods = dict.fromkeys((
            'ACK', 'BYE', 'CANCEL', 'INFO', 'INVITE', 'MESSAGE', 'NOTIFY',
            'OPTIONS', 'PRACK', 'PUBLISH', 'REFER', 'REGISTER', 'SUBSCRIBE',
            'UPDATE'
        ))
        __proto = 'SIP'

        def unpack(self, buf):
            f = StringIO(buf)
            line = f.readline()
            l = line.strip().split()
            if len(l) != 3 or l[0] not in self.__methods or not l[2].startswith(self.__proto):
                raise SipUnpackError(f'invalid request: {line}')
            self.method = l[0]
            self.uri = l[1]
            self.version = l[2][len(self.__proto) + 1:]
            Message.unpack(self, f.read())

        def __str__(self):
            return f'{self.method} {self.uri} {self.__proto}/{self.version}\r\n'  + Message.__str__(self)


class Response(Message):
    """SIP response."""

    __hdr_defaults__ = {
        'version': '2.0',
        'status': '200',
        'reason': 'OK',
        'headers': {'to': '', 'from': '', 'call-id': '', 'cseq': '', 'contact': ''}
    }
    __proto = 'SIP'

    def unpack(self, buf):
        f = StringIO(buf)
        line = f.readline()
        l_strip = line.strip().split(None, 2)
        if len(l_strip) < 2 or not l_strip[0].startswith(self.__proto) or not l_strip[1].isdigit():
            raise SipUnpackError('invalid response: %r' % line)
        self.version = l_strip[0][len(self.__proto) + 1:]
        self.status = l_strip[1]
        self.reason = l_strip[2]
        Message.unpack(self, f.read())

    def __str__(self):
        return '%s/%s %s %s\r\n' % (self.__proto, self.version, self.status,
            self.reason) + Message.__str__(self)

class AllPLFuncs(PLRESP, PLREQ):
     
    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
class AllStFunsc():
     
    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        pass

        
def gen_request(side='platform', **kwargs):
    count = kwargs.pop('count')
    for i in range(count):
        func = kwargs.pop('func')
        if side == 'station':
            ps = AllStFunsc(**kwargs)
        else:
            ps = AllPLFuncs(**kwargs)
        if func not in ps.funcs:
            pprint(f"ERROR: {func} not in reqiure func {ps.funcs} list")
            return
        request = run_func(ps, func, **kwargs)
    try:
        req = Request(request)
    except SipUnpackError as e:
        # pprint("ERROR: malformed SIP Request. %s\n" % e)
        req = Response(request)
    if "cseq" not in req.headers:
        req.headers["cseq"] = f"{i} {req.method}"
    yield str(req)


def print_reply(buf, out_regex=None, out_replace=None):
    src_ip = buf[1][0]
    src_port = buf[1][1]
    try:
        resp = Response(buf[0].decode())
    except SipUnpackError as e:
        resp = Request(buf[0].decode())
    pprint(str(resp))
    if resp.__class__.__name__ == "Response":
        resp.status
        resp.reason
        out_regex = '(.*\n)*'
        if resp.__class__.__name__ == "Request":
            out_replace = f"received Request {resp.method} {resp.uri} from {src_ip}:{src_port}\n"
        else:
            out_replace = f"received Response {resp.status} {resp.reason} from {src_ip}:{src_port}\n"

    if True:
        out = ''
        try:
            out = re.sub(out_regex, out_replace, "%s" % resp)
            # print(out)
            pprint(out)
        except Exception as e:
            pprint(f"ERROR: an issue is occoured applying regex substitution:\n\t{e.__str__()}\n" \
                         f"\t-----------------------------------\n\tRegex: {out_regex}\n" \
                         f"\tSubstitution string: {out_replace}\n\tSubstitution text: {out}\n")
            pprint("\tResponse: \n")
            pprint("\t-----------------------------------\n\t")
            pprint("\n\t".join(resp.__str__().split("\n")))
            pprint("-----------------------------------\n")
            pprint(resp)
        return True

def b_protocol_data_send(sock, dest, wait, **kwargs):
    dest_ip, dest_port = dest
    sent = rcvd = 0
    side = kwargs.pop('from_side', 'platform')
    try:
        for req in gen_request(side=side, **kwargs):
            pprint(req)
            try:
                try:
                    sip_req = Request(req)
                    pprint(f"Sent Request {sip_req.method} to {dest_ip}:{dest_port} cseq={sip_req.headers['cseq'].split()[0]} len={len(str(sip_req))}")
                except Exception as e:
                    sip_req = Response(req)
                    pprint(f"Receive from={sip_req.headers['from']} body={sip_req.body} cseq={sip_req.headers['cseq'].split()[0]} len={len(str(sip_req))}")
                # Add Content-Lenght if missing
                if "content-length" not in sip_req.headers:
                    sip_req.headers["content-length"] = len(sip_req.body)

                try:
                    sock.sendto(bytes(str(sip_req), 'utf-8'), (dest_ip, dest_port))
                except Exception as e:
                    pprint(f"ERROR: cannot send packet to {dest_ip}:{dest_port} {e.__str__()}")
                
                pprint("=== Full Request Sent ===")
                pprint(f"\n{sip_req}")
                sent += 1
            except socket.timeout:
                pass
            time.sleep(wait)
            yield req
    except KeyboardInterrupt:
        pass

    pprint('--- statistics ---')
    pprint(f'{sent} packets transmitted, {rcvd} packets received, {(float(sent - rcvd) / sent) * 100} packet loss')
    pprint('--- statistics ---')
    pprint(f'{sent} packets transmitted, {rcvd} packets received, {(float(sent - rcvd) / sent) * 100} packet loss')



