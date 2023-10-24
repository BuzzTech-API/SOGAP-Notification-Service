import mimetypes
import os
from fastapi import FastAPI, UploadFile
from google.cloud import storage

## Google cloud storage service
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcs-key.json'

class GCStorage:
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket_name = 'buzz_tech'

    async def upload_file(self,file):
        try:
            if file: #Verifica se o arquivo existe

                #Obtem o bucket do gcs define o caminho do arquivo no bucket e cria um novo blob
                bucket = self.storage_client.get_bucket(self.bucket_name)
                file_path = "buzz_tech/" + file.filename
                blob = bucket.blob(file_path)

                #Detecta o tipo do arquivo
                mime_type, encoding = mimetypes.guess_type(file.filename)

                #Faz o upload do arquivo para o blob
                blob.upload_from_file(file.file, content_type=mime_type)

                return f'https://storage.cloud.google.com/{self.bucket_name}/{file_path}' #Retorna a URL do arquivo no gcs
        
            else:
                return 'O arquivo está vazio'
            
        except Exception as e:
            return str(e)