import os
import json
import azure.storage.blob
from azure.identity import ClientSecretCredential

class AzureCli:
    def __init__(self, account_name, container_name, account_url, client_id, client_secret, tenant_id):
        self.account_name = account_name
        self.container_name = container_name
        self.account_url = account_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def connect_to_storage_account(self):
        credential = ClientSecretCredential(client_id=self.client_id, client_secret=self.client_secret, tenant_id=self.tenant_id)
        blob_service = azure.storage.blob.BlobServiceClient(account_url=self.account_url, account_name=self.account_name, credential=credential)
        container_client = blob_service.get_container_client(self.container_name)
        return container_client

    def store_json_in_blob(self, json_object, blob_name):
        # Convert the JSON object to a string
        blob_text = json.dumps(json_object)
        
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(blob_text, overwrite=True)

    def get_json_from_blob(self, blob_name):
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_text = blob_client.download_blob().readall()
        json_object = json.loads(blob_text)
        return json_object

    def get_blob_list(self):
        container_client = self.connect_to_storage_account()
        blob_list = container_client.list_blobs()
        return blob_list

    def delete_blob(self, blob_name):
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def get_blob_url(self, blob_name):
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_url = blob_client.url
        return blob_url

    def get_blob_name_from_url(self, blob_url):
        blob_name = blob_url.split('/')[-1]
        return blob_name    

    def get_blob_url_from_name(self, blob_name):
        blob_url = self.account_url + "/" + self.container_name + "/" + blob_name
        return blob_url 




