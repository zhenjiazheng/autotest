from tools import open_sock, listen_sock
from tools.sipping.sipping import b_protocol_data_send
from app.services.tools import Tools

if __name__ == '__main__':
    client_ip = "10.9.114.4"
    client_port = 6000
    platform_ip = "10.9.114.4"
    platform_port = 5900
    kwargs = {"platform_ip": platform_ip, "platform_port": platform_port, "platform_code": "091600000000000000", 
              "sip_auth_password":"12345", "station_code": "091600000100000000", 
              "station_cam_code":"0916000001030100XX", "station_ip": client_ip, "station_port":client_port,
              "count": 1, "func": "request_resource", "index":1, "start":0, "end":1}
    _, sock = open_sock(platform_ip, 5900, 1)
    # b_protocol_data_send(sock=sock, dest=(platform_ip, platform_port), wait=1, **kwargs)

    # kwargs.update({'func': 'register'})
    # b_protocol_data_send(sock=sock, dest=(platform_ip, platform_port), wait=1, **kwargs)
    
    for rcv in listen_sock(sock):
        print(rcv)
        Tools.response_for_req_data(rcv, "{}")