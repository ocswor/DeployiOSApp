# -*- coding: utf-8 -*-
# @Time    : 2017/12/1 下午3:09
# @Author  : Eric

#!/usr/bin/env python
#coding: utf-8

# sendEmail title content
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr, COMMASPACE
from config import *


def _format_addr(s):
    name, addr = parseaddr(s)
    name = Header(name, 'utf-8').encode()
    addr = addr.encode('utf-8') if isinstance(addr, unicode) else addr
    return formataddr((name, addr))

def send_mail(title, content):

    try:
        msg = MIMEText(content,'plain','utf-8')
        if not isinstance(title,unicode):
            title = unicode(title, 'utf-8')
        msg['Subject'] = title
        msg['From'] = sender
        msg['To'] = COMMASPACE.join([_format_addr(u'%s <%s>' % (to.split("@")[0], to)) for to in receiver])
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        smtp = smtplib.SMTP_SSL(smtpserver,465)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
        print "邮件发送成功!"
        return True
    except Exception, e:
        print str(e)
        print "邮件发送失败!"
    return False