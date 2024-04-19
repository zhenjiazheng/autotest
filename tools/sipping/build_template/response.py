#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
from .base import BaseParam

class PlatformResponseRegister(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)

    def register_auth(self, **kwargs):
        return f"""SIP/2.0 401 Unauthorized 
Via: SIP/2.0/UDP {self.station_ip}:{self.station_port};rport={self.station_port};branch=z9hG4bK 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 1 REGISTER 
WWW-Authenticate: Digest realm="{self.platform_ip}",nonce="9bd055", algorithm=MD5 
Content-Length: 0
"""

    def register_auth_404(self, **kwargs):
        return f"""SIP/2.0 404 User unknown 
Via: SIP/2.0/UDP {self.station_ip}:{self.station_port};rport={self.station_port};branch=z9hG4bK 
To: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=2c101e0
Call-ID: c47ecb12 
CSeq: 1 REGISTER 
Content-Length: 0
"""

    def register(self, **kwargs):
        expires = kwargs.get('expires', 80)
        dt = datetime.datetime.now()
        date = dt.isoformat(timespec='milliseconds')
        return f"""SIP/2.0 200 OK
Via: SIP/2.0/UDP {self.station_ip}:{self.station_port};rport={self.station_port};branch=z9hG4bK 
To: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 2 REGISTER 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>;expires={expires}
Date: {date}
Content-Length: 0
"""

class PlatformResponseNotify(BaseParam):
    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
    def notify(self, **kwargs):
        index = kwargs.get('index', 1)
        return f"""SIP/2.0 200 OK
Via: SIP/2.0/UDP {self.station_ip}:{self.station_port};rport={self.station_port};branch=z9hG4bK 
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=f2161243 
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: {index} NOTIFY
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}> 
Content-Length: 0
"""

class PlatformResponse(PlatformResponseRegister, PlatformResponseNotify):
     
    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)

    def pic_receive_resp(self): 
        return f"""HTTP/1.1 200 OK 
Date: Sat, 31 Dec 2023 23:59:59 GMT 
Content-Type: text/html;charset=ISO-8859-1 
Content-Length: 0"""
