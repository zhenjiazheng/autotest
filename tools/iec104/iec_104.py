import re
from .config import *
from .asdu_type import *
import time
import queue
import datetime
import threading
import binascii
import socket


def control_field_number(cf):
    decimal_1 = int(cf[0], 16)
    bits_1 = bin(decimal_1)[2:].zfill(8)
    decimal_2 = int(cf[1], 16)
    bits_2 = bin(decimal_2)[2:].zfill(8)
    integer = int(bits_2 + bits_1[: -1], 2)
    return integer


def print_result(data=None, address=None, qb=None, date=None):
    if address:
        print(f'IOA {address}', end=line_separator)
    result = ''
    if data is not None:  # need to print even if data == 0
        result += f'value: {data}\n'
    if qb:
        result += f', quality bid: {qb}\n'
    if date:
        result += f', date: {date}\n'
    print(result)
    return result


class TCPSocket:

    def __init__(self, logger, addr, waiting=5):
        """Create an IP Physical Layer.
        :addr tuple: Address tuple (host, port)
        """
        self.logger = logger
        self.addr = addr
        self.connection = None
        self.connected = False
        self.alive = threading.Event()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.read_port)
        self.waiting = waiting
        self.logger.debug("New IP with addr %s", addr)

    def connect(self):
        """Connect to `self.addr`
        """
        self.connection = socket.create_connection(self.addr)
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.connected = True
        self.alive.set()
        self.thread.start()
        self.logger.debug(f"Connection with {self.addr} created, wait {self.waiting}")
        time.sleep(self.waiting)

    def disconnect(self):
        """Disconnects
        """
        self.alive.clear()
        self.thread.join(5)
        self.logger.debug("Thread joined..")
        if self.connection:
            self.connection.close()
        self.connected = False
        self.logger.debug("Disconnected from %s", self.addr)

    def read_port(self):
        """Read bytes from socket
        """
        self.logger.debug("Start reading port for %s", self.addr)
        self.connection.settimeout(10.0)
        while self.alive.is_set():
            try:
                response = self.connection.recv(16)
            except socket.timeout as e:
                continue
            except Exception as e:
                continue
            if not response:
                continue
            self.logger.debug(
                "<= Reading %s from %s",
                binascii.hexlify(response),
                self.addr
            )
            for byte_resp in response:
                self.queue.put(byte_resp)
        self.logger.debug("Stopping reading port for %s", self.addr)
        self.queue.put(None)

    def send_byte(self, byte):
        """Send a byte"""
        assert isinstance(self.connection, socket.socket)
        self.logger.debug("=> Sending %02x to %s", byte, self.addr)
        self.connection.send(bytes([byte]))

    def send_bytes(self, bts):
        assert isinstance(self.connection, socket.socket)
        self.logger.info("=> Sending %s to %s", binascii.hexlify(bts), self.addr)
        print("=> Sending %s to %s", binascii.hexlify(bts), self.addr)
        self.connection.send(bts)
        self.logger.info("=> Send %s to %s finished", binascii.hexlify(bts), self.addr)
        print("=> Send %s to %s finished", binascii.hexlify(bts), self.addr)

    def get_byte(self, timeout=5):
        """Read a byte"""
        # logger.info("Getting byte. waiting {}".format(timeout))
        if not self.queue.empty():
            return self.queue.get(True, timeout=timeout)


class Iec101_4:
    def __init__(self,logger, message):
        self.msg = ''
        self.logger = logger
        self.error = False
        message = re.findall('[A-Fa-f0-9]{2}', message)  # parse octets in list
        self.message = [i.upper() for i in message]
        self.message_bytes = self.message[6:-2]
        self.length = int((self.message[2] + self.message[1]), 16) 
        if len(self.message_bytes) < 4:  # minimal length of telegram 4
            self.error = True
            self.logger.error(f'message to short {len(self.message_bytes)} octets')
            self.msg =+ f"Error: message to short {len(self.message_bytes)} octets\n"
            return
        self.start = self.message[0]
        # self.length = self.message[1]
        self.control_field = self.message_bytes[1: 5]
        if self.start != '68':  # 104 telegram start octet must equal 68
            self.error = True
            self.logger.error('package must start with 68')
            self.msg =+ "Error: package must start with 68\n"
            return
        elif self.length != len(self.message_bytes):  # second octet is length of telegram
            self.error = True
            return
        if self.length > 4:  # S-type and U-type have length 4. I-type always longer
            self.type_identification = self.message[6]
            self.asdu_type = ASDU_TYPE[self.type_identification]
            self.SQ = byte_to_dec(self.message[7], stop=1)
            self.number_of_objects = byte_to_dec(self.message[7], start=1)
            self.test = byte_to_dec(self.message[8], stop=1)
            self.pos_neg = byte_to_dec(self.message[8], start=1, stop=2)
            self.COT = byte_to_dec(self.message[8], start=2)
            self.ORG = self.message[9]
            self.COA = self.message[11] + self.message[10]
            type_length = sum([information_elements_length[i] for i in self.asdu_type['format']])  # length of inf objects base on elements in type
            if self.SQ:  # SQ mean only first inf object have address, next +1 from previous
                self.objects = [self.message[12: (12 + type_length + 3)]]  # first inf object with 3 octets address
                self.objects += [self.message[(12 + 3 + i * type_length): (12 + 3 + (i + 1) * type_length)]
                                 for i in range(1, self.number_of_objects)]  # all following without address
            else:
                type_length += 3  # plus 3 octets to inf object length for address
                self.objects = [self.message[(12 + i * type_length): (12 + (i + 1) * type_length)]
                                for i in range(self.number_of_objects)]

    def report_s_type(self):
        if BODY and not HEAD:
            self.logger.info('U format not have ASDU')
            self.msg += 'U format not have ASDU\n'
            return
        self.logger.info('S format')
        self.msg += 'S format\n'
        self.logger.info(f'Receive sequence {control_field_number(self.control_field[2:])}')
        self.msg += f'Receive sequence {control_field_number(self.control_field[2:])}\n'

    def report_u_type(self):
        if BODY and not HEAD:
            self.logger.info('U format not have ASDU')
            self.msg += 'U format not have ASDU\n'
            return
        self.logger.info('U format')
        self.msg += 'U format\n'
        self.logger.info(u_type_dict[self.control_field[0]])
        self.logger.info(f'Send sequence {control_field_number(self.control_field[:2])}')
        self.msg += f'Send sequence {control_field_number(self.control_field[:2])}\n'
        self.logger.info(f'Receive sequence {control_field_number(self.control_field[2:])}')
        self.msg += f'Receive sequence {control_field_number(self.control_field[2:])}\n'

    def report_i_type(self):
        self.logger.info('I format\n')
        if HEAD or not (HEAD or BODY):
            if self.number_of_objects != len(self.objects):
                self.msg += 'mismatch Number of objects'
                return print('mismatch Number of objects\n')
            self.logger.info(f'Send sequence {control_field_number(self.control_field[:2])}')
            self.msg += f'Send sequence {control_field_number(self.control_field[:2])}\n'
            self.logger.info(f'Receive sequence {control_field_number(self.control_field[2:])}')
            self.msg += f'Receive sequence {control_field_number(self.control_field[2:])}\n'
            self.logger.info(f'Type identification {self.type_identification}, ({int(self.type_identification, 16)})')
            self.msg += f'Type identification {self.type_identification}, ({int(self.type_identification, 16)})\n'
            self.logger.info(f'{self.asdu_type["reference"]}, {self.asdu_type["format"]}')
            self.msg += f'{self.asdu_type["reference"]}, {self.asdu_type["format"]}\n'
            self.logger.info(f'SQ {self.SQ}')
            self.msg += f'SQ {self.SQ}\n'
            self.logger.info(f'Number of objects {self.number_of_objects}')
            self.msg += f'Number of objects {self.number_of_objects}\n'
            try:
                self.logger.info(f'COT {self.COT}, {cot_dict[self.COT]}')
                self.msg += f'COT {self.COT}, {cot_dict[self.COT]}\n'
            except IndexError as e:
                self.logger.info(f'ERROR: unknown COT {self.COT}, ({int(self.COT, 16)})')
                self.msg += f'ERROR: unknown COT {self.COT}, ({int(self.COT, 16)})\n'
            self.logger.info(f'ORG {self.ORG}')
            self.msg += f'ORG {self.ORG}\n'
            self.logger.info(f'COA {self.COA} ({int(self.COA, 16)})')
            self.msg += f'COA {self.COA} ({int(self.COA, 16)})\n'
        if BODY or not (HEAD or BODY):
            for x in self.objects:
                self.logger.info('Information Element\n')
                self.msg += 'Information Element\n'
                self.logger.info(x)
                self.msg += str(x) + "\n"
                result = print_result(**self.asdu_type['func'](x))
                self.msg += result
        # print('\n')

    def report(self):
        if self.error:
            self.logger.error(f'mismatch length of APDU and telegram length {int(self.length, 16)} != {(len(self.message) - 2)}')
            self.msg += f'ERROR: mismatch length of APDU and telegram length {int(self.length, 16)} != {(len(self.message) - 2)}\n'
            return
        if byte_to_dec(self.control_field[0], 6) == 1 and self.length == 4:  # if last to bits is 1 -> is S type telegram
            self.report_s_type()
        elif byte_to_dec(self.control_field[0], 6) == 3 and self.length == 4:  # elif last to bits is 3 -> is U type telegram
            self.report_u_type()
        else:  # else -> is I type telegram
            self.report_i_type()


class IEC104(object):

    def __init__(self, logger, typ, date,  vsq=1, cot=3, pub_addr='0100', info_addr=2336, status='10') -> None:
        """
        : arg type (str): 'S' or 'C' for sensor or controller
        : arg date (str): datetime in format
        : arg vsq (int): number of the objects
        : arg cot (int): cause reason
        : arg pub_addr (str): public address of the device
        : arg info_addr (str): information address of the device
        : arg status (str): status of the device, '11' for online and '00' for offline
        """
        self.typ = typ
        self.date = date
        self.vsq = vsq
        self.cot = cot
        self.info_element = status
        self.pub_addr = pub_addr
        self.info_addr = info_addr
        self.logger = logger

    def double_to_CP56Time2a(self):
        # prepare CP56Time2a time
        dt = self.date if self.date else datetime.datetime.now()
        ml = int((int(dt.second) * 1000) + (int(dt.microsecond) / 1000))
        min = int(dt.minute)
        hrs = int(dt.hour)
        day = int(((int(dt.weekday()) + 1) * 32) + int(dt.strftime("%d")))
        mon = int(dt.month)
        yr = int(dt.strftime("%y"))
        data = ml.to_bytes(2,'little') + min.to_bytes(1,'little') + hrs.to_bytes(1,'little') + day.to_bytes(1,'little') + mon.to_bytes(1,'little') + yr.to_bytes(1,'little')
        return data.hex()

    def int2double_point(self, val, length=6):
        st = hex(val).replace('x', '0')
        leng = len(st)
        if leng > length:
            all_str = st[-length:]
        else:
            all_str = "0" * (length - leng) + st
        all_str = re.findall(r'.{2}', all_str)
        all_str.reverse()
        return ''.join(all_str)

    def int2cot(self, val):
        hx = hex(val).replace('x', '0')
        return hx[-2:]
    
    def int2typ(self, val):
        return self.int2cot(val)

    def get_crc(self, asdu):
        asdu_sp = re.findall(r'.{2}', asdu)
        # aa = ['1f', '02', '09', '00', '01', '00', '00', '00', '00', '00', '3e', 'e6', '00', '11', '98', '08', '17', 'ff', 'ff', '00', '00',
        #       '3e', 'e6', '00', '11', '98', '08', '17']
        crc = sum(list([int(each, 16) for each in asdu_sp]))
        print(crc)
        return self.int2cot(crc)
    
    def get_asdu_length(self, asdu_data):
        length = len(asdu_data) / 2
        asdu_len = self.int2double_point(int(length), 4)
        return asdu_len
        # macth = {10: "a", 11: "b", 12: "c", 13: "d", 14: "e", 15: 'f'}
        # ct = int(length % 16)
        # # 整个ASDU的长度
        # asdu_len = f'{int(length / 16)}{macth[ct] if ct > 9 else str(ct)}'
        # return asdu_len + '00'
    
    # 组装101 header + 104规约报文数据
    def build_104_message(self):
        # 组装104规约报文数据
        start = '68'
        vsq = self.int2cot(self.vsq)
        cot = self.int2cot(self.cot) + '00'
        info_addr = self.int2double_point(self.info_addr)
        typ = self.int2typ(self.typ)
        asdu_addr = f'{typ}{vsq}{cot}{self.pub_addr}'
        infos = ''
        info_element = str(hex(int(self.info_element, 2)).replace('x', '0'))[1:]
        for _ in range(self.vsq):
            cp56time2a = self.double_to_CP56Time2a()
            info = info_addr + info_element + cp56time2a
            infos += info 
        # cp56time2a2 = self.double_to_CP56Time2a()
        # info = info_addr + self.info_element + cp56time2a2
        # 整个ASDU
        asdu_data = asdu_addr + infos
        self.logger.info(f"IEC104 ASDU Part: {asdu_data}")
        crc = self.get_crc(asdu_data)
        self.logger.info(f"CRC Check {crc}")
        # 整个ASDU的长度
        # 整个ASDU的长度
        asdu_len = self.get_asdu_length(asdu_data)
        self.logger.info(f"ASDU Length Part: {asdu_len}")
        # 报文头部分（固定长度）101 部分
        message_header = f'{start}{asdu_len * 2}{start}'
        self.logger.info(f"IEC101 Header Part: {message_header}")
        # 报文尾部分（固定长度）101 部分
        message_ending = f'{crc}16'
        message_data = message_header + asdu_data + message_ending
        message = re.findall(r'.{2}', message_data)
        message_data = " ".join(message)
        self.logger.info(f"Hex Data {message_data}")
        return message_data


def main():
    while True:
        telegram = Iec101_4(input('type package:\n'))
        telegram.report()


def iec104_send_data(logger, dst, array):
    socket = TCPSocket(logger, dst) 
    try:
        socket.connect()
        data = bytearray.fromhex(array)
        socket.send_bytes(data)
        time.sleep(3)
    except:
        return '', -1
    finally:
        socket.disconnect()
    

def iec104_test(logger, dst, date, typ=31, vsq=1, cot=3, info_addr=2336, status='10'):
    """
    :arg cot: random.choice(range(1, 10)) default 3
    :arg point: random.choice(range(1, 65535)) default '2336'
    :arg value: random.choice(['00', '01', '10', '11']) default '11'
    :return: str

    This function generates a random test case for the given problem.
    The function will generate a random integer between 1 and 9 (cot) and a random integer between 1 and 65534 (point).
    It will also generate a random value from the list ['00', '01', '10', '11'].
    Finally, it will return the generated values as a string in
    """
    # cot 选择:
    # 0	0x00	未用				
    # 1	0x01	周期、循环 （遥测）				
    # 2	0x02	背景扫描（遥信）（遥测）				
    # 3	0x03	突发(自发) （遥信）（遥测）				
    # 4	0x04	初始化完成				
    # 5	0x05	请求或者被请求（遥信被请求）（遥测被请求）				
    # 6	0x06	激活（激活）（遥控、参数设置 控制方向）				
    # 7	0x07	激活确认（激活确认）（遥控、参数设置 监视方向）				
    # 8	0x08	停止激活 （遥控、参数设置 控制方向）				
    # 9	0x09	停止激活确认（遥控、参数设置 监视方向）				
    # 10 0x0a	激活终止 （遥控 监视方向）				
    # 13 0x0d	文件传输				
    # 20 0x14	响应站召唤（总召唤）（遥信响应总召唤）（遥测响应总召唤）				
    # 44 0x2c	未知的类型标识（遥控、参数设置 监视方向）				
    # 45 0x2d	未知的传送原因（遥控、参数设置 监视方向）				
    # 46 0x2e	未知的应用服务数据单元公共地址（遥控、参数设置 监视方向）				
    # 47 0x2f	未知的信息对象地址（遥控、参数设置 监视方向）				
    # 48 0x30	遥控执行软压板状态错误				
    # 49 0x31	遥控执行时间戳错误				
    # 50 0x32	遥控执行数字签名认证错误	

    # info_addr 取值范围:  random.choice(range(1, 65535)	
    
    # status 取值范围：  ['00', '01' '10', '11']
    result = False
    msg = ''
    iec = IEC104(logger, date=date, typ=typ, vsq=vsq, cot=cot, pub_addr='0100', info_addr=info_addr, status=status)
    try:
        data = iec.build_104_message()
        # print(data)
        telegram = Iec101_4(logger, data)
        telegram.report()
        msg = telegram.msg
        result = iec104_send_data(logger, dst, data)
    except:
        return True, data, msg
    return result, data, msg


# if __name__ == '__main__':
#     main()
#     # =========================================================================
#     array =  [
#             # iec 101 header
#             '68', # start
#             '1c', # apdu len,
#             '00', '1c', '00', # len + 3 =  control_field
#             # iec 104 asdu layer
#             '68', # start
#             '1f', # type id: M_ST_TB_1(31)
#             '02', # SQ
#             '03', # test and pos_neg and cot
#             '00', # ORG
#             '01', '00', # COA
#             '00', '00', '00', '00', '00', '00', '00', '08', '21', '01', '31', # indeterminate data
#             '36', # CRC check
#             '16' # iec 101 ending
#         ]
#     print(array)
#     # 测试代码
#     # COT random.choice(range(1, 10)) Default 3
#     # POINT random.choice(range(1, 65535)) Default 2336
#     # Value ['00', '01' '10', '11'] Default "11"
#     dst = ('0.0.0.0', 2410)
#     point = random.choice(range(2330, 2700))
#     value = random.choice(['00', '01' '10', '11'])
#     iec104_test(dst, count=3, cot=3, point=point, value=value)