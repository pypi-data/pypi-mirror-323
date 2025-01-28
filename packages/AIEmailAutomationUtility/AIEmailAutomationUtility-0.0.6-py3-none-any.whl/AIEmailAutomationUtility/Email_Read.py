import imaplib
import email
import os
import json
import time
import loggerutility as logger
from flask import Flask, request
from .Save_Transaction import Save_Transaction
from .Email_Upload_Document import Email_Upload_Document

class Email_Read:
    def read_email(self, email_config):
        try:
            logger.log("inside function")
            mail = imaplib.IMAP4_SSL(email_config['host'], email_config['port'])
            mail.login(email_config['email'], email_config['password'])
            logger.log("login successfully")
            mail.select('inbox')

            while True:
                status, email_ids = mail.search(None, 'UNSEEN')
                emails = []
                
                if status == 'OK':
                    email_ids = email_ids[0].split()

                    if not email_ids: 
                        logger.log("Email not found, going to check new mail")
                        print("Email not found,\ngoing to check new mail \n")
                    else:
                    
                        for email_id in email_ids:
                            email_body = ""
                            attachments = []
                            status, data = mail.fetch(email_id, '(RFC822)')
                            
                            if status == 'OK':
                                raw_email = data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                sender_email = msg['From']
                                cc_email = msg['CC']
                                subject = msg['Subject']
                                to = msg['To']

                                if msg.is_multipart():
                                    for part in msg.walk():
                                        content_type = part.get_content_type()
                                        if content_type == "text/plain":
                                            email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                                else:
                                    email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              

                                email_data = {
                                    "email_id": email_id,
                                    "from": sender_email,
                                    "to": to,
                                    "cc": cc_email,
                                    "subject": subject,
                                    "body": email_body
                                }
                                emails.append(email_data)
                                logger.log(f"emails:: {emails}")
                                call_save_transaction = Save_Transaction()
                                save_transaction_response = call_save_transaction.email_save_transaction(email_data)
                                logger.log(f"save_transaction_response:: {save_transaction_response}")

                                if save_transaction_response['status'] == "Success":
                                    if msg.is_multipart():
                                        for part in msg.walk():
                                            content_disposition = str(part.get("Content-Disposition"))

                                            if "attachment" in content_disposition: 
                                                attachment_path = self.save_attachment(part, "attachments")
                                                if attachment_path:
                                                    logger.log(f"Attachment saved at: {attachment_path}")
                                                    attachments.append(attachment_path)
                                    for file_path in attachments:
                                        logger.log(f"file_path:: {file_path}")
                                        email_upload_doc = Email_Upload_Document()
                                        email_file_upload = email_upload_doc.upload_files(file_path)
                                        logger.log(f"file uploaded :: {email_file_upload}")
                        logger.log(f"emails:: {emails}")
                time.sleep(10)
        
        except Exception as e:
            return {"success": "Failed", "message": f"Error reading emails: {str(e)}"}
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception as close_error:
                logger.log(f"Error during mail close/logout: {str(close_error)}")

    def save_attachment(self, part, download_dir):
        try:
            filename = part.get_filename()
            if filename:
                # Create the directory if it doesn't exist
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                file_path = os.path.join(download_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                logger.log(f"Attachment saved: {file_path}")
                return file_path
        except Exception as e:
            return {"success": "Failed", "message": f"Error saving attachment: {str(e)}"}

    def Read_Email(self):
        try:
            data = request.get_data('jsonData', None)
            data = json.loads(data[9:])
            logger.log(f"jsondata:: {data}")

            reciever_email_addr = data.get("reciever_email_addr")
            receiver_email_pwd = data.get("receiver_email_pwd")
            host = data.get("host")
            port = data.get("port")

            if not all([reciever_email_addr, receiver_email_pwd, host, port]):
                raise ValueError("Missing required email configuration fields.")

            logger.log(f"\nReceiver Email Address: {reciever_email_addr}\t{type(reciever_email_addr)}", "0")
            logger.log(f"\nReceiver Email Password: {receiver_email_pwd}\t{type(receiver_email_pwd)}", "0")
            logger.log(f"\nHost: {host}\t{type(host)}", "0")
            logger.log(f"\nPort: {port}\t{type(port)}", "0")

            email_config = {
                'email': reciever_email_addr,
                'password': receiver_email_pwd,
                'host': host,
                'port': int(port)
            }

            emails = self.read_email(email_config)            
            logger.log(f"Read_Email response: {emails}")

        except Exception as e:
            logger.log(f"Error in Read_Email: {str(e)}")

        

