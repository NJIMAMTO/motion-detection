import os
from smtplib import SMTP
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
 
import configparser

#=======#configファイルの読み込み#=======#
config = configparser.ConfigParser()
config_ini_path = "mailing.ini"
config.read(config_ini_path, encoding="utf-8")

# SMTP認証情報
account = config['MAILSETTING']['account']
password = config['MAILSETTING']['password']
 
# 送受信先
to_email = config['MAILSETTING']['to_email']
from_email = config['MAILSETTING']['from_email']
#=======#configファイルの読み込み 終わり#=======#

def SendMail(zipfile):
    # MIMEの作成
    msg = MIMEMultipart()

    subject = "This is the recorded security camera footage"
    message = "recorded security camera"

    msg["Subject"] = subject
    msg["To"] = to_email
    msg["From"] = from_email
    body = MIMEText(message, "html")
    msg.attach(body)

    # 添付ファイルの設定
    basename = os.path.basename(zipfile)
    attach_file = {'name': basename, 'path': zipfile}
    attachment = MIMEBase('aplication', 'zip')
    file = open(attach_file['path'], 'rb+')
    attachment.set_payload(file.read())
    file.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=attach_file['name'])
    msg.attach(attachment)

    # メール送信処理
    try:
        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(account, password)
        server.send_message(msg)
        server.quit()
        print("Successfully sent email")
    except Exception:
        print("Error: unable to send email")

if __name__ == "__main__":
    SendMail('test')
