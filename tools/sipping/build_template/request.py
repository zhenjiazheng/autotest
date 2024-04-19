
#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .base import BaseParam


class PlatformRequestMessage(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)

    def request_resource(self, **kwargs):
        # 平台请求获取资源
        # B.3.4.1 请求获取资源
        index = kwargs.get('index', 1)
        start = kwargs.get('start', 1)
        end = kwargs.get('end', 2)
        body = f"""<?xml version="1.0" encoding="UTF-8"?>
<SIP_XML EventType=Request_Resource> 
    <Item Code="{self.station_cam_code}" FromIndex="{start}" ToIndex="{end}"/>
</SIP_XML>"""
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} MESSAGE
Content-Type: application/xml 
Content-Length: {length}

{body}"""

    def request_history_alarm(self, index, alarm_type, begin_time, end_time, level, start_index, end_index, **kwargs): 
        # 平台发起告警事件查询请求
        # B.4.4.1 告警事件查询请求
        index = kwargs.get('index', 1)
        alarm_type = kwargs.get('alarm_type')
        begin_time = kwargs.get('begin_time')
        end_time = kwargs.get('end_time')
        level = kwargs.get('level')
        start_index = kwargs.get('start_index', 1)
        end_index = kwargs.get('end_index', 2)
        body = f"""<?xml version="1.0" encoding="UTF-8"?> 
<SIP_XML EventType=Request_History_Alarm> 
    <Item Code="{self.station_cam_code}" UserCode="{self.station_code}" Type= "{alarm_type}" 
    BeginTime="{begin_time}" EndTime="{end_time}" Level="{level}" FromIndex="{start_index}" ToIndex="{end_index}"/>
</SIP_XML>"""
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} MESSAGE
Content-Type: application/xml 
Content-Length: {length}

{body}
"""
    def request_history_video(self, **kwargs):
        # 平台发起录像检索请求
        # B.5.4.1 录像检索请求
        index = kwargs.get('index', 1)
        alarm_type = kwargs.get('alarm_type')
        begin_time = kwargs.get('begin_time')
        end_time = kwargs.get('end_time')
        level = kwargs.get('level')
        start_index = kwargs.get('start_index', 1)
        end_index = kwargs.get('end_index', 2)
        body = f"""<?xml version="1.0" encoding="UTF-8"?> 
<SIP_XML EventType=Request_History_Video> 
    <Item Code="{self.station_cam_code}"  Type= "{alarm_type}" UserCode="{self.station_code}" 
    BeginTime="{begin_time}" EndTime="{end_time}" Level="{level}" FromIndex="{start_index}" ToIndex="{end_index}"/>
</SIP_XML>"""
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} MESSAGE
Content-Type: application/xml 
Content-Length: {length}

{body}
"""

    def video_playback_control(self, **kwargs):
        # B.10.5.3 录像回放控制-播放
        index = kwargs.get('index', 1)
        body = f"""PLAY RTSP/1.0 
Session: 123456 
CSeq: 2
Range: ntp=10-28"""
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47k42 
CSeq: {index} MESSAGE 
Content-Type: application/rtsp 
Content-Length: {length}

{body}
"""

    def control_camera(self, index, command, params, **kwargs):
        # B.8.4.1 云镜控制请求
        index = kwargs.get('index', 1)
        command = kwargs.get('command')
        params = kwargs.get('params', [])
        param_str = []
        for index, param in enumerate(params, 1):
            param_str.append(f'CommandPara{index}="{param}"')
        body=f""""<?xml version="1.0" encoding="UTF-8"?>
<SIP_XML EventType=”Control_Camera”>
    <Item Code="{self.station_cam_code}" command="{command}" {" ".join(param_str)} />
</SIP_XML>"""
        length = len(body)

        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} MESSAGE
Content-Type: application/xml
Content-Length: {length}
 
{body}"""

    def camera_snap(self, **kwargs):
        # B.11.4.1 图片抓拍请求
        index = kwargs.get('index', 1)
        pic_server = kwargs.get('pic_server')
        snap_type = kwargs.get('snap_type')
        range = kwargs.get('range')
        interval = kwargs.get('interval', 30)
        body = f"""<?xml version="1.0" encoding="UTF-8"?> 
<SIP_XML EventType=Camera_Snap>
    <Item Code="{self.station_cam_code}" PicServer="{pic_server}" SnapType="{snap_type} Range="{range}", Interval="{interval}" />
</SIP_XML>""" 
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} MESSAGE
Content-Type: application/xml 
Content-Length: {length}

{body}"""

class PlatformRequestInvite(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
    def video_realtime_play(self, **kwargs):
        # 调阅实时视频
        # B.6.4.1 调阅实时视频请求
        index = kwargs.get('index', 1)
        body = f"""v=0 
o=- 0 0 IN IP4 {self.platform_ip}
s=Play 
c=IN IP4 {self.station_ip}
m=audio 13578 RTP/AVP 8100
a=rtpmap:100 H264/90000 
a=fmtp:100 CIF=1;4CIF=1;F=1;K=1 
a=rate:main 
a=sendrecv"""
        length = len(body)
        return f"""INVITE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} INVITE
Content-Type: application/sdp
Content-Length: {length}

{body}"""

    def audio_talk(self, **kwargs):
        # B.7.4.1 语音会话请求
        index = kwargs.get('index', 1)
        body = f"""v=0 
o=- 0 0 IN IP4 {self.platform_ip}
s=Talk 
c=IN IP4 {self.station_ip}
m=audio 38564 RTP/AVP 8 
a=rtpmap:8 PCMA/8000
a=sendrecv"""
        length = len(body)
        return f"""INVITE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} INVITE
Content-Type: application/sdp
Content-Length: {length}

{body}"""

    def video_playback(self, **kwargs):
        # B.10.4.1 录像回放请求
        # B.10.5.1 录像回放请求
        index = kwargs.get('index', 1)
        rtsp = kwargs.get('rtsp', '')
        body = f"""v=0 
o=- 0 0 IN IP4 {self.platform_ip}
s=Playback 
u={rtsp} 
c=IN IP4 {self.station_code}
m=video 10000 RTP/AVP 100 
y=1234456 
a=rtpmap:100 H264/90000 
a=fmtp:100 CIF=1;4CIF=1;F=1;K=1 
a=recvonly"""


        length = len(body)
        return f"""INVITE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} INVITE
Content-Type: application/sdp
Content-Length: {length}

{body}"""

class PlatformRequestSubscribe(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)

    def subscribe_alarm(self, **kwargs):
        # B.9.1.4.1 订阅告警事件请求
        index = kwargs.get('index', 1)
        event_dict = kwargs.get('event_dict', {})
        events = ""
        for k, v in event_dict.items():
            events += f"""   <Item Code="{k}" Type="{v}" />"""
        body = f"""<?xml version="1.0" encoding="UTF-8"?> 
<SIP_XML EventType=Subscribe_Alarm>
{events}
</SIP_XML>"""
        length = len(body)
        return f"""SUBSCRIBE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} SUBSCRIBE
Event: alarm 
Expires: 4200 
Max-Forwards: 70 
Content-Type: application/xml 
Content-Length: {length}

{body}
"""

    def subscribe_status(self, **kwargs): 
        # B.9.1.4.2 订阅状态事件请求
        index = kwargs.get('index', 1)
        addr_code = kwargs.get('addr_code')
        body = f"""<?xml version="1.0" encoding="UTF-8"?> 
<SIP_XML EventType=Subscribe_Status>
    <Item Code="{addr_code}">
</SIP_XML>"""
        length = len(body)
        return f"""SUBSCRIBE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: {index} SUBSCRIBE
Event: presense 
Expires: 4200 
Max-Forwards: 70 
Content-Type: application/xml 
Content-Length: {length}

{body}
"""

class PlatformRequest(PlatformRequestMessage, PlatformRequestInvite, PlatformRequestSubscribe):
    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                        station_code, station_cam_code, station_ip, station_port, **kwargs)
