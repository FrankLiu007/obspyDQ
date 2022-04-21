#!/usr/bin/python3
# coding:utf-8
import sys
import smtplib

from email.mime.text import MIMEText
from email.header import Header


def send_email(email_par, req):
    """
    警告，此处的邮件发送服务不能保证发送成功
    如果想确保成功，可以使用第三方邮件服务器，或者自行搭建
    这里没有使用第三方邮件服务器发送，原因在于会有数量的限制，当然也可以将所有请求合并为一个邮件
    此外关于直接集成邮箱发送服务都python的设想在此处有参考:
    https://stackoverflow.com/questions/50695188/what-is-the-proper-way-to-actually-send-mail-from-python-code
    :param email_par:
    :param req:
    :return:
    """
    msg = MIMEText(req, _subtype='plain')
    msg['From'] = email_par["sender"]
    msg['To'] = email_par["receiver"]
    msg['Subject'] = Header(email_par["subject"])

    smtp = smtplib.SMTP('iris.washington.edu:25')
    # smtp = smtplib.SMTP()
    # smtp.connect(email_par["smtpserver"])
    # smtp.login(email_par["username"], email_par["password"])
    smtp.sendmail(email_par["sender"], email_par["receiver"], msg.as_string())
    smtp.quit()
