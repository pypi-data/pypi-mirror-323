import os
import json
import shutil
import requests
import loggerutility as logger
from flask import Flask,request


class Email_DocumentUploader:
    def upload_document(self, upload_config, file_data):
        # try:
        logger.log("inside function" )
        # Create temp directory if needed
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Save file temporarily
        file_path = os.path.join(temp_dir, file_data['filename'])
        logger.log(f"file_path:: {file_path}")
        with open(file_path, 'wb') as f:
            f.write(file_data['content'])
        
        # Prepare headers and parameters
        headers = {"TOKEN_ID": upload_config["token_id"]}
        params = {}
        
        param_fields = {
            "DOCUMENT_TYPE": "document_type",
            "OBJ_NAME": "obj_name",
            "FILE_TYPE": "file_type",
            "APP_ID": "app_id"
        }
        logger.log(f"param_fields:: {param_fields}")
        
        for api_key, config_key in param_fields.items():
            if config_key in upload_config and upload_config[config_key]:
                params[api_key] = upload_config[config_key]
        
        # Upload file
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.request(
                upload_config["method"],
                upload_config["url"],
                headers=headers,
                files=files,
                data=params
            )
        logger.log("file read")
        
        if response.status_code == 200:
            result = json.loads(response.text)
            document_id = result["ID"]["Document_Id"]
            return str(response.status_code), document_id
        else:
            return str(response.status_code), f"Upload failed: {response.text}"
                
        # except Exception as e:
        #     logger.log(f"Error uploading document: {str(e)}")
        #     raise
        # finally:
        #     # Cleanup
        #     if os.path.exists(temp_dir):
        #         shutil.rmtree(temp_dir)

    def email_document_upload(self):
        try:
            if 'file' not in request.files:
                return "file not found"
                
            file = request.files['file']
            if file.filename == '':
                return "No selected file"

            upload_config = {
                'token_id': request.form.get('TOKEN_ID'),
                'document_type': request.form.get('DOCUMENT_TYPE', ''),
                'obj_name': request.form.get('OBJ_NAME', ''),
                'file_type': request.form.get('FILE_TYPE', ''),
                'app_id': request.form.get('APP_ID', ''),
                'method': request.form.get('Method_Type', 'POST'),
                'url': request.form.get('RestAPI_Url')
            }

            # Validate required fields
            if not upload_config['token_id'] or not upload_config['url']:
                return "Missing required fields: TOKEN_ID or RestAPI_Url"
            
            file_data = {
                'filename': file.filename,
                'content': file.read()
            }

            result = self.upload_document(upload_config, file_data)
            
            logger.log(f"Upload_Document response result: {result}")
            return "success"

        except Exception as e:
            logger.log(f"Error in Upload_Document: {str(e)}")