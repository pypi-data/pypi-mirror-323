import hashlib
import os

from typing import Dict, IO, Optional
from werkzeug.utils import secure_filename

from .abc import AwsClient

class S3(AwsClient):
  @property
  def service_name(self) -> str:
    return "s3"
  
  def download(
    self,
    bucket_name: str,
    object_key: str,
    file_path: str,
  ) -> None:
    """
    Download an S3 object to a file.
    
    Args:
      bucket_name: The name of the bucket containing the object.
      object_key: The key of the object to download.
      file_path: The path to save the downloaded object to.
    """
    with open(file_path, "wb") as file:
      self.client.download_fileobj(bucket_name, object_key, file)
  
  @classmethod
  def file2prefix(cls, file_path: str, splits: int=4) -> str:
    """
    Generate an S3 object key prefix from a file.
    
    Args:
      file_path: The path to the file to generate a prefix for.
      splits: The number of path components to include in the prefix.
    
    Returns:
      A prefix for an S3 object key.
    """
    # Calculate SHA-256 hash of the file
    with open(file_path, "rb") as file:
      sha256 = hashlib.file_digest(file, "sha256").hexdigest()
      
    # Split the hash into chunks
    chunks = [sha256[i:i+2] for i in range(0, 2*(splits - 1), 2)]
    return f"{'/'.join(chunks)}/{sha256[2*(splits - 1):]}"
  
  def upload(
    self,
    file_path: str,
    bucket_name: str,
    object_key_prefix: str,
    metadata: Optional[Dict[str, str]] = None,
  ) -> str:
    """
    Upload a file to an S3 bucket.
    
    Args:
      file_path: The path to the file to upload.
      bucket_name: The name of the bucket to upload the file to.
      object_key_prefix: The prefix to use for the object key. 
      metadata: Optional metadata to attach to the object.
      
    Returns:
      The object key of the uploaded object.
    """
    object_key = f"{object_key_prefix}/{secure_filename(os.path.basename(file_path))}"
    
    self.client.upload_file(
      file_path,
      bucket_name,
      object_key,
      ExtraArgs={"Metadata": metadata} if metadata else None
    )
    
    return object_key
  
  def get_metadata(
    self,
    bucket_name: str,
    object_key: str,
  ) -> Dict[str, str]:
    """
    Get the metadata for an S3 object.
    
    Args:
      bucket_name: The name of the bucket containing the object.
      object_key: The key of the object to get metadata for.
    
    Returns:
      A dictionary containing the object's metadata.
    """
    return self.client.head_object(Bucket=bucket_name, Key=object_key)["Metadata"]
  
  def create_presigned_get(
    self,
    bucket_name: str,
    object_key: str,
    expiration: int=3600,
  ) -> str:
    """
    Generate a presigned URL for downloading an S3 object.
    
    Args:
      bucket_name: The name of the bucket containing the object.
      object_key: The key of the object to generate a presigned URL for.
      expiration: The number of seconds the URL should be valid for.
    
    Returns:
      A presigned URL for downloading the object.
    """
    return self.client.generate_presigned_url(
      "get_object",
      Params={"Bucket": bucket_name, "Key": object_key},
      ExpiresIn=expiration
    )
  
  def create_presigned_post(
    self,
    bucket_name: str,
    object_key: str,
    expiration: int=3600,
  ) -> Dict[str, str]:
    """
    Generate a presigned URL for uploading an object to an S3 bucket.
    
    Args:
      bucket_name: The name of the bucket to upload the object to.
      object_key: The key to use for the uploaded object.
      fields: A dictionary of form fields to include in the presigned URL.
      expiration: The number of seconds the URL should be valid for.
    
    Returns:
      A dictionary containing the presigned URL and form fields.
    """
    return self.client.generate_presigned_post(
      bucket_name,
      object_key,
      ExpiresIn=expiration
    )