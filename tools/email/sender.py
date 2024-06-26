#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

from config import PublicEmailConfig
from utils import get_funs, run_func



smtp_server = PublicEmailConfig.Server
user = PublicEmailConfig.User
password = PublicEmailConfig.Password
mail_port = PublicEmailConfig.EmailPort


class HTMLTemplate:
    STYLE = """
    <style type="text/css" media="screen">
     body {
          background: url("/static/images/timg2.jpg") center top no-repeat;
          background-size: 100% 100%;
          background-attachment: fixed;
          height: 500px;
          min-height: 450px;
          font-size: 20px;
          font-weight: 500;
          color: #5d7399;
          margin:0;padding:0;border:0;
        }
     table.gridtable {
          font-family: verdana,arial,sans-serif;
          font-size: 12px;
          font-weight: 800;
          color: #5d7399;
        }
     table.gridtable th {
          text-align: center;
          width: 100%
          padding: 12px;
          border-style: solid;
          border-color: #666666;
          background-color: #dedede;
          
          }
     table.gridtable td {
          width: 100%
          padding: 12px;
          border-style: solid;
          border-color: #666666;
          background-color: #ffffff;
          }
    </style>
"""
    
    def __init__(self):
        self.__get_funs()

    def __get_funs(cls):
        cls.funcs = get_funs(cls)

    def ssh(cls, ip, user, password, message, **kwargs):
        return f"""
<html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
            <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
            {cls.STYLE}
            <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
            <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
        </head>
        <body>
            <h1>类型：SSH连接失败稳定性异常结果通知<br/></h1>
            Dear ALL,<br/>
            <br/>
            以下是SSH连接失败稳定性测试异常通知: <br/>
            &emsp;IP: {ip}<br/>
            &emsp;User: {user}<br/>
            &emsp;Password: {password}<br/>
            原因： SSH 连接重试10间隔10S后仍然无法连接, 测试停止退出, 测试失败。 <br/><br/>

            Message: {message}
            这是一封自动发送的邮件，并且不会回复任何邮件！请勿回复...<br/>
            为了提高阅览体验，建议使用Chrome浏览器！<br />
        </body>
</html>
"""

    def docker(cls, ip, user, password, message, **kwargs):
        return  f"""
<html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
            <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
            {cls.STYLE}
            <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
            <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
        </head>
        <body>
            <h1>类型: Docker容器--服务运行稳定性异常结果通知<br/></h1>
            Dear ALL,<br/>
            <br/>
            以下是后端部署服务-Docker稳定性测试异常通知: <br/>
            异常原因： SSH 检查Docker服务仍然正常运行，过程:重试10间隔10S后, Docker服务仍然没有运行起来。 <br/><br/>
            以下是SSH 检查设备: <br/>
            &emsp;IP: {ip}<br/>
            &emsp;User: {user}<br/>
            &emsp;Password: {password}<br/><br/>
            &emsp;Message: {message} <br/><br/>
            这是一封自动发送的邮件，并且不会回复任何邮件！请勿回复...<br/>
            为了提高阅览体验，建议使用Chrome浏览器！<br />
        </body>
</html>
"""

    def hw(cls, ip, user, password, hw_type, limit_value, hw_charts, **kwargs):
        return  f"""
<html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
            <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
            {cls.STYLE}
            <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
            <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
        </head>
        <body>
            <h1>类型：{hw_type}预警--超过最大限制结果通知<br/></h1>
            Dear ALL,<br/>
            <br/>
            以下是性能测试-{hw_type}预警--超过最大限制结果通知: <br/>
            异常原因： SSH 检查 硬件资源{hw_type} 超过预期最大值使用率: {limit_value}。 <br/><br/>
            以下是SSH 检查设备: <br/>
            &emsp;IP: {ip}<br/>
            &emsp;User: {user}<br/>
            &emsp;Password: {password}<br/>
            硬件HTML图表: {hw_charts}<br/>
            这是一封自动发送的邮件，并且不会回复任何邮件！请勿回复...<br/>
            为了提高阅览体验，建议使用Chrome浏览器！<br />
        </body>
</html>
"""

    def report(cls, ip, user, password, charts, **kwargs):
        return  f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
        {cls.STYLE}
        <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
        <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    </head>
    <body>
        <h1>BM硬件资源监控执行完成<br/></h1>
        Dear ALL,<br/>
        <br/>
        以下是SSH 检查设备: <br/>
        &emsp;IP: {ip}<br/>
        &emsp;User: {user}<br/>
        &emsp;Password: {password}<br/><br/>
        <p>硬件HTML图表列表:</p><br/>
        {charts}
        这是一封自动发送的邮件，并且不会回复任何邮件！请勿回复...<br/>
        为了提高阅览体验，建议使用Chrome浏览器！<br />
    </body>
</html>
"""

def gen_template(**kwargs):

    host = f"http://{os.environ.get('HOST')}:{os.environ.get('PORT')}"
    tp = HTMLTemplate()
    if kwargs.get('type').lower() == 'hw':
        hw_charts = kwargs.get('hw_charts')
        new_chart = f'<a href="{host}/autotest/report/perf_result/{hw_charts}">{hw_charts.split(os.sep)[-1]}</a>'
        kwargs.update({"hw_charts": new_chart})
    elif kwargs.get('type').lower() == 'report':
        charts = kwargs.get('charts')
        new_charts = []
        for chart in charts:
            new_charts.append(f'<a href="{host}/autotest/report/perf_result/{chart}">{chart.split(os.sep)[-1]}</a>')
        in_charts = '<br>\n'.join(new_charts)+'<br>'
        kwargs.update({"charts": in_charts})

    return run_func(tp, kwargs.get('type').lower(), **kwargs) 


def send_email(**kwargs):
    """
    This function takes in recipient and will send the email to that email address with an attachment.
    """
    mail_to = kwargs.get('mail_to')
    if not mail_to:
        return
    try:
        html = gen_template(**kwargs)
    except Exception as e:
        print(e.__str__())
        return  
    time_str = time.strftime("%Y-%m-%d", time.localtime())
    # Set the server and the message details
    # Create the multi-part
    msg = MIMEMultipart()
    msg['Subject'] = f"检测结果-{kwargs.get('type')}-{time_str}"
    msg['From'] = user
    msg['To'] = ",".join(mail_to) if isinstance(mail_to, list) else mail_to  # recipient

    # msg preamble for those that do not have a email reader
    msg.preamble = 'MultiPart message.\n'
    # Text part of the message
    html = MIMEText(html, 'html', _charset='utf-8')
    msg.attach(html)
    try:
        sp = smtplib.SMTP(host=smtp_server)
        sp.connect(host=smtp_server, port=mail_port)
    except:
        sp = smtplib.SMTP()
        sp.connect(smtp_server, mail_port)
    # Start the server
    sp.set_debuglevel(0)
    # sp.ehlo()
    sp.starttls()
    sp.login(user, password)
    receive_address = list(set(mail_to))
    sp.sendmail(msg['From'], receive_address, msg.as_string())
    sp.quit()
    print("Send Report Successfully.")

