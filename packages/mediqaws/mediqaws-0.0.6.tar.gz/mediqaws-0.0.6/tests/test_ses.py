import os

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from mediqaws.clients import Ses

def test_send_raw_email():
  message = MIMEMultipart()
  message["From"] = (Header(os.getenv("EMAIL_FROM_NAME"), "utf-8").encode()
                    + f" <{os.getenv('EMAIL_FROM_ADDR')}>")
  message["To"] = (Header(os.getenv("EMAIL_TO_NAME"), "utf-8").encode()
                  + f" <{os.getenv('EMAIL_TO_ADDR')}>")
  message["Subject"] = os.getenv("EMAIL_SUBJECT")
  message.attach(MIMEText(os.getenv("EMAIL_TEXTBODY"), "plain"))
  
  with Ses(profile_name=os.getenv("AWS_PROFILE_NAME")) as ses:
    response = ses.send_raw_email(message.as_string())
  print(response)
  assert response["ResponseMetadata"]["HTTPStatusCode"] == 200