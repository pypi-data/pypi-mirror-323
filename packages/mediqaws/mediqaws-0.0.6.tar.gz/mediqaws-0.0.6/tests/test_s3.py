import json
import os
import pytest
import requests

from datetime import datetime, timezone

from mediqaws.clients import S3
from tests import data_dir, output_dir

profile_name = os.getenv("AWS_PROFILE_NAME")
bucket_name = os.getenv("S3_BUCKET_NAME")
data_file = os.path.join(data_dir, "mixed.json")
object_key_prefix = S3.file2prefix(data_file)
print(f"object_key_prefix: {object_key_prefix}")

@pytest.fixture
def setup_client():
  with S3(profile_name=profile_name) as s3:
    yield s3
    
def test_upload_and_download(setup_client):
  s3 = setup_client
  
  timestamp = datetime.now(timezone.utc).isoformat()
  
  object_key = s3.upload(
    data_file,
    bucket_name,
    object_key_prefix,
    metadata={"timestamp": timestamp},
  )
  print(f"object_key: {object_key}")
  assert object_key == f"{object_key_prefix}/mixed.json"
  
  # Get the metadata for the object
  meta = s3.get_metadata(bucket_name, object_key)
  print(f"meta: {meta}")
  assert "timestamp" in meta and meta["timestamp"] == timestamp
  
  download_file = os.path.join(output_dir, "downloaded.json")
  
  # Remove download file if it exists
  if os.path.exists(download_file):
    os.remove(download_file)
  
  s3.download(bucket_name, object_key, download_file)
  assert os.path.exists(download_file)
  assert S3.file2prefix(download_file) == object_key_prefix
  
  # Clean up
  os.remove(download_file)
  response = s3.client.delete_object(Bucket=bucket_name, Key=object_key)
  assert response["ResponseMetadata"]["HTTPStatusCode"] == 204
  
def test_presigned_post_and_get(setup_client):
  s3 = setup_client
  
  object_key = f"{object_key_prefix}/presigned.json"
  
  # Remove object first
  s3.client.delete_object(Bucket=bucket_name, Key=object_key)
    
  # Generate a presigned URL for uploading
  presigned_post = s3.create_presigned_post(bucket_name, object_key)
  print(f"presigned_post: {presigned_post}")
  
  with open(data_file, "rb") as f:
    files = {"file": (os.path.basename(data_file), f)}
    response: requests.Response = requests.post(
      presigned_post["url"],
      data=presigned_post["fields"],
      files=files,
    )
  assert response.status_code == 204
  
  # Generate a presigned URL for downloading
  url = s3.create_presigned_get(bucket_name, object_key)
  print(f"presigned_get: {url}")
  
  response = requests.get(url)
  assert response.status_code == 200
  
  download_file = os.path.join(output_dir, "presigned.json")
  
  # Remove download file if it exists
  if os.path.exists(download_file):
    os.remove(download_file)
  
  with open(download_file, "wb") as f:
    f.write(response.content)
  
  assert os.path.exists(download_file)
  assert S3.file2prefix(download_file) == object_key_prefix
  
  # Clean up
  os.remove(download_file)
  response = s3.client.delete_object(Bucket=bucket_name, Key=object_key)
  assert response["ResponseMetadata"]["HTTPStatusCode"] == 204
