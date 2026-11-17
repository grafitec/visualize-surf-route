from dotenv import load_dotenv
import os
from pathlib import Path
import imaplib
import smtplib
import email
import json
import traceback
from email.message import EmailMessage

def initiate_mail_client():
    env_path = (
            Path(__file__).parent.parent
            / "config"
            / "mail_settings.env"
    )
    load_dotenv(env_path)

    email_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_address, password)

    return mail

def get_new_mails():
    mail = initiate_mail_client()
    mail.select("TrackToMp4")
    status, messages = mail.search(
        None,
        "ALL"
    )
    mail_ids = messages[0].split()

    dataFromMail = []
    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id,"(RFC822)")
        message = email.message_from_bytes(msg_data[0][1])
        print(message["Subject"])
        if message["Subject"] and message["Subject"].lower() == "tracktomp4":

            jsonData = None
            fileName = None

            for part in message.walk():
                content_type = part.get_content_type()
                filename = part.get_filename()

                if content_type == "text/plain" and not filename:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset)
                        jsonData = json.loads(body)

                if filename and filename.endswith(".tcx"):
                    filepath = (
                            Path(__file__).parent.parent
                            / "data"
                            / "tcx"
                    )
                    filepath.mkdir(parents=True, exist_ok=True)
                    for num in range(20):
                        fileName = (Path(filepath) / f"appleWatchRideData_rideId_untracked{num}.tcx")
                        if not os.path.exists(fileName):
                            break

                    with open(fileName, "wb") as file:
                        file.write(part.get_payload(decode=True))
                    jsonData['filepath'] = fileName
        dataFromMail.append(jsonData)
    print('Read '+str(len(dataFromMail))+" mails")
    return dataFromMail
    return dataFromMail

def move_mail(label):
    try:
        mailId = b'1'
        mail = initiate_mail_client()
        mail.select(label)
        mail.copy(mailId, "Used "+label.lower())

        mail.store(mailId, '+FLAGS', '\\Deleted')

        mail.expunge()
    except Exception:
        traceback.print_exc()

def send_mail(outputnames):
    env_path = (
            Path(__file__).parent.parent
            / "config"
            / "mail_settings.env"
    )
    load_dotenv(env_path)

    password = os.getenv("EMAIL_PASSWORD")
    email_address = os.getenv("EMAIL_ADDRESS")

    # Skapa mejlet
    msg = EmailMessage()
    msg["From"] = f"TrackToMp4 script<{email_address}>"
    msg["To"] = email_address
    msg["Subject"] = "Surftrack rendered files"
    msg.set_content('Here are the files')
    for outputname in outputnames:
        with open(outputname[1], "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=Path(outputname[1]).name
            )


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as mail:
        mail.login(email_address, password)
        mail.send_message(msg)