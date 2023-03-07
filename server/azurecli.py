"""
This module contains the AzureCli class which is used to connect to 
Azure Storage and store and retrieve JSON objects
"""
import os
import json
import azure.storage.blob
from azure.identity import ClientSecretCredential


class AzureCli:
    """
    This class is used to interact with the Azure Storage API
    """
    # Set these values to your storage account and container
    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    tenant_id = os.environ.get("AZURE_TENANT_ID")

    def __init__(self):
        return

    def connect_to_storage_account(self):
        """
        Connect to the Azure Storage account
        """
        credential = ClientSecretCredential(
            client_id=self.client_id, client_secret=self.client_secret, tenant_id=self.tenant_id)
        blob_service = azure.storage.blob.BlobServiceClient(
            account_url=self.account_url, account_name=self.account_name, credential=credential)
        container_client = blob_service.get_container_client(
            self.container_name)
        return container_client

    def store_json_in_blob(self, json_object, blob_name):
        """
        Store a JSON object in a blob
        """
        # Convert the JSON object to a string
        blob_text = json.dumps(json_object)

        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(blob_text, overwrite=True)

    def get_json_from_blob(self, blob_name):
        """
        Get a JSON object from a blob
        """
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_text = blob_client.download_blob().readall()
        json_object = json.loads(blob_text)
        return json_object

    def get_blob_list(self):
        """
        Get a list of blobs in the container
        """
        container_client = self.connect_to_storage_account()
        blob_list = container_client.list_blobs()
        return blob_list

    def delete_blob(self, blob_name):
        """
        Delete a blob
        """
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def get_blob_url(self, blob_name):
        """
        Get the URL of a blob
        """
        container_client = self.connect_to_storage_account()
        blob_client = container_client.get_blob_client(blob_name)
        blob_url = blob_client.url
        return blob_url

    def get_blob_name_from_url(self, blob_url):
        """
        Get the name of a blob from its URL
        """
        blob_name = blob_url.split('/')[-1]
        return blob_name

    def get_blob_url_from_name(self, blob_name):
        """
        Get the URL of a blob from its name
        """
        blob_url = self.account_url + "/" + self.container_name + "/" + blob_name
        return blob_url
