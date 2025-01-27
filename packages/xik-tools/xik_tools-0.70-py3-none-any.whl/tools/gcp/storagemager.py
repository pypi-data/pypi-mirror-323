import logging
from google.cloud import storage
from google.oauth2 import service_account
from datetime import timedelta

class StorageManager:
    def __init__(self, credentials_file=None):
        if credentials_file is not None:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
            logging.info("Credentials loaded successfully.")
            self.client = storage.Client(credentials=self.credentials)
        else:
            self.client = storage.Client()
        logging.info("Google Cloud Storage client initialized successfully.")

    def upload_file(self, bucket_name, file_path, destination_blob_name):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        logging.info(f"File {file_path} uploaded to {destination_blob_name}.")

    def download_file(self, bucket_name, blob_name, destination_file_path):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_file_path)
        logging.info(f"File {blob_name} downloaded to {destination_file_path}.")

    def list_files_in_bucket(self, bucket_name):
        bucket = self.client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        return [blob.name for blob in blobs]

    def make_file_public(self, bucket_name, blob_name):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.make_public()
        logging.info(f"File {blob_name} is publicly accessible at: {blob.public_url}")
        return blob.public_url

    def generate_signed_url(self, bucket_name, blob_name, expiration=3600):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        signed_url = blob.generate_signed_url(
            expiration=timedelta(seconds=expiration),
            method="GET"
        )
        logging.info(f"Generated signed URL: {signed_url}")
        return signed_url

    def bucket_exists(self, bucket_name):
        try:
            self.client.get_bucket(bucket_name)
            logging.info(f"Bucket {bucket_name} exists.")
            return True
        except Exception as e:
            logging.error(f"Bucket {bucket_name} does not exist: {e}")
            return False

    def get_public_url_if_file_exists(self, bucket_name, file_name):
        """
        버킷에서 파일명을 검색하여 존재하면 공개 URL을 반환하는 함수

        Args:
        bucket_name (str): 검색할 버킷 이름
        file_name (str): 검색할 파일 이름

        Returns:
        str: 파일이 존재하면 공개 URL 반환, 없으면 None 반환
        """
        try:
            bucket = self.client.get_bucket(bucket_name)
            blobs = bucket.list_blobs()

            for blob in blobs:
                if blob.name == file_name:
                    # 파일이 존재하면 공개 URL 확인 또는 생성
                    if not blob.public_url:
                        blob.make_public()
                    logging.info(f"File {file_name} found. Public URL: {blob.public_url}")
                    return blob.public_url
            
            logging.info(f"File {file_name} not found in bucket {bucket_name}.")
            return None
        except Exception as e:
            logging.error(f"Error while checking for file: {e}")
            return None
