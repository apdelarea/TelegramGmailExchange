#Get emails and send to telegram.
#this will run in cron.

import imaplib
import email
from email.header import decode_header
import os
import webbrowser
import requests
import re
 
imap = imaplib.IMAP4_SSL("imap.gmail.com")  # establish connection
 
imap.login("aris.chatbot@gmail.com", " ")  # login
 
#print(imap.list())  # print various inboxes
status, messages = imap.select("INBOX")  # select inbox
 
numOfMessages = int(messages[0]) # get number of messages
 
 
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)
 
def obtain_header(msg):
    # decode the email subject
    messID = msg["Message-ID"]
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding)
 
    # decode email sender
    From, encoding = decode_header(msg.get("From"))[0]
    if isinstance(From, bytes):
        From = From.decode(encoding)
 
    #print("Subject:", subject)
    #print("From:", From)
    return subject, re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", From)[0], messID
 
def download_attachment(part):
    # download attachment
    filename = part.get_filename()
 
    if filename:
        folder_name = clean(subject)
        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the subject)
            os.mkdir(folder_name)
            filepath = os.path.join(folder_name, filename)
            # download attachment and save it
            open(filepath, "wb").write(part.get_payload(decode=True))

def send_to_telegram(message):

    apiToken = '5746068823:AAEiok7m-OTfOUsk9wiOflA52l9EvHW9cc8'
    chatID = '-861121448'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)



for i in range(numOfMessages, numOfMessages - 10, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")  # fetches the email using it's ID
 
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
 
            subject, From, messID = obtain_header(msg)
 
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    regex = re.compile(r'<[^>]+>')
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
 
                    try:
                        body = regex.sub('', part.get_payload(decode=True).decode())
                    except:
                        pass
 
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        #print(body)
                        pass
                    elif "attachment" in content_disposition:
                        download_attachment(part)
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    #print(body)
                    pass
 
            print("="*100)

        #print(subject)
        #print(From)
        #print(body)

        #to monitor email that will be duplicated.
        if (os.path.exists("processedemails.txt")):
           pass
        else:
           f = open("processedemails.txt", "w")
           f.close()
          
        f = open("processedemails.txt")
        #print(str(f).find(messID))
        if (str(f.read()).find(messID) >= 0):
          f.close()
          pass
        else:
          #send to TG
          send_to_telegram("From: " + From + "\n" + "Subject: " + subject + "\n" + "Message: " + body)
          #record in processed emails.
          f.close()
          f = open("processedemails.txt", "a")
          f.writelines(messID+"\n")
          f.close()
 
imap.close()

#send_to_telegram("Hello from Python!")
