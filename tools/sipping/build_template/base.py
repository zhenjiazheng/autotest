from utils import get_funs


commands = {
    "0x0504": "左转", "0x0601": "预置位保存","0x0602":"预置位调用", "0x0603": "预置位删除", 
    "0x0701": "左上方向运动停止", "0x0702": "左上方向运动", "0x0703": "左下方向运动停止","0x0704": "左下方向运动", 
    "0x0801": "右下方向运动停止","0x0802": "右下方向运动", "0x0803": "右上方向运动停止","0x0804": "右上方向运动",
    "0x0901": "停止当前动作","0x0a01": "雨刷开", "0x0a02": "雨刷关",
    "0x0b01": "灯亮", "0x0b02": "灯灭", "0x0c01": "加热开", "0x0c02": "加热关", "0x0d01": "红外开", "0x0d02": "红外关",
    "0x0e01": "线性扫描开始", "0x0e02": "线性扫描停止", "0x0f01": "轨迹巡航开始", "0x0f02": "轨迹巡航停止",
    "0x1001": "预置位巡航开始", "0x1002": "预置位巡航停止", "0x1101": "云台锁定", "0x1102": "云台解锁"
    }

alarms_type = {"0": "视频丢失告警", "1": "移动侦测告警", "2": "视频遮挡告警", "8": "设备高温告警", "9": "设备低温告警", 
               "10": "风扇故障告警", "11": "磁盘故障告警", "16": "状态时间告警"} 




class BaseParam:
    ## 视频（B接口）例子：
    ## IP地址： 10.130.141.233
    ## 端口号： 5090
    ## 平台编码（SIP）：091600000000000000
    ## SIP认证密码：12345
    ## 前端系统编码（站端需要提供）091600000100000000
    ## 摄像机编码（站段需要提供）0916000001030100XX

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs):

        self.platform_ip = platform_ip
        self.platform_port = platform_port
        self.platform_code = platform_code
        self.sip_auth_password = sip_auth_password
        self.station_code = station_code 
        self.station_cam_code = station_cam_code
        self.station_ip = station_ip
        self.station_port = station_port
        self.__get_funs()

    def __get_funs(cls):
        cls.funcs = get_funs(cls)

class ReceiveRegister(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
    def register(self, **kwargs):
        expires = kwargs.get('expires', 3600)
        return f"""REGISTER sip:{self.platform_ip}:{self.platform_port} SIP/2.0
Via: SIP/2.0/UDP {self.station_code}:{self.station_ip};rport={self.station_port};branch=z9hG4bK 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 1 REGISTER 
Expires: {expires}
Content-Length: 0
"""

    def register_auth(self, **kwargs):
        expires = kwargs.get('expires', 3600)
        return f"""REGISTER sip:{self.platform_ip}:{self.platform_port} SIP/2.0
Via: SIP/2.0/UDP {self.station_code}:{self.station_ip};rport={self.station_port};branch=z9hG4bK 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 2 REGISTER 
Expires: {expires}
Authorization: Digest username="{self.station_code}",realm="{self.station_code}",nnotallow="9bd055",
uri="sip:{self.platform_ip}",respnotallow="5924f86c43",algorithm=MD5
Content-Length: 0
"""

    def register_refresh(self, **kwargs):
        expires = kwargs.get('expires', 3600)
        return f"""REGISTER sip:{self.platform_ip}:{self.platform_port} SIP/2.0
Via: SIP/2.0/UDP {self.station_code}:{self.station_ip};rport={self.station_port};branch=z9hG4bK 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 8 REGISTER 
Expires: {expires}
Authorization: Digest username="{self.station_code}",realm="{self.station_code}",nnotallow="9bd055",
uri="sip:{self.platform_ip}",respnotallow="5924f86c43",algorithm=MD5
Content-Length: 0
"""

    def register_logut_out(self, **kwargs):
        return f"""REGISTER sip:{self.platform_ip}:{self.platform_port} SIP/2.0
Via: SIP/2.0/UDP {self.station_code}:{self.station_ip};rport={self.station_port};branch=z9hG4bK 
Contact: <sip: {self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.platform_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243 
From: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>;tag=2c101e0 
Call-ID: c47ecb12 
CSeq: 20 REGISTER 
Authorization: Digest username="{self.station_code}",realm="{self.station_code}",nnotallow="9bd055",
uri="sip:{self.platform_ip}",respnotallow="5924f86c43",algorithm=MD5
Logout-Reason: "maintenance"
Content-Length: 0
"""

class ReceiveMessage(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
    def response_resource(self, **kwargs):
        # 平台请求获取资源
        # B.3.4.1 请求获取资源
        start = kwargs.get('start', 1)
        end = kwargs.get('end', 2)
        body = f"""<?xml versinotallow="1.0" encoding="UTF-8"?>
<SIP_XML EventType=Response_Resource>
    <SubList Code="{self.station_cam_code}" RealNum="1" SubNum=1 FromIndex=1 ToIndex=2>
        <Item Code=”地址编码” Name=”名称” Status=”节点状态值” DecoderTag=”解码插件标签” Longitude=”经度值” Latitude=”纬度值” SubNum=”包含的字节点数目”/>
    </SubList>
</SIP_XML>
"""
        length = len(body)
        return f"""MESSAGE sip:{self.station_ip}:{self.station_port} SIP/2.0
Via: SIP/2.0/UDP {self.platform_ip}:{self.platform_port};branch=z9hG4bK
From: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>;tag=f2161243
To: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Contact: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Call-ID: c47a42
CSeq: 1 MESSAGE
Content-Type: application/xml 
Content-Length: {length}
{body}"""

class Receive(BaseParam):

    def __init__(self, platform_ip, platform_port, platform_code, sip_auth_password, 
                 station_code, station_cam_code, station_ip, station_port, **kwargs) -> None:
        super().__init__(platform_ip, platform_port, platform_code, sip_auth_password, 
                         station_code, station_cam_code, station_ip, station_port, **kwargs)
        
    def receive_default(self): 
        return f"""OPTIONS sip:{self.platform_ip}:{self.platform_port} SIP/2.0
Via: SIP/2.0/UDP {self.station_ip}:{self.station_port}
Max-Forwards: 70
From: "fake" <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
To: <sip:{self.station_code}@{self.platform_ip}:{self.platform_port}>
Contact: <sip:{self.station_code}@{self.station_ip}:{self.station_port}>
Call-ID: c47a42
Date: Wed, 24 Apr 2013 20:35:23 GMT
Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, SUBSCRIBE, NOTIFY, INFO, PUBLISH
Supported: replaces, timer"""



if __name__ == '__main__':
    resp = Receive()
    resp.funcs