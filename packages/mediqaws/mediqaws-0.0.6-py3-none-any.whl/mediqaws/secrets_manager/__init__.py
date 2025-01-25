import boto3
import json
import time
from botocore.exceptions import ClientError

class SecretsManager:
  def __init__(self):
    self.client = boto3.client("secretsmanager")
    self.cache = {}
    self.timestamps = {}
    self.ttl = 3600 # Time-to-live in seconds
    
  def get_secret(self, secret_name: str) -> str:
    current_time = time.time()
    
    # Check if the secret is in the cache and not expired
    if secret_name in self.cache and current_time - self.timestamps[secret_name] < self.ttl:
      return self.cache[secret_name]
    
    # Fetch the secret from AWS Secrets Manager
    try:
      response = self.client.get_secret_value(SecretId=secret_name)
      secret = response.get("SecretString") or response.get("SecretBinary")
      if isinstance(secret, str):
        try:
          secret = json.loads(secret)
        except json.JSONDecodeError:
          pass
        
      # Cache the secret for the next ttl seconds
      self.cache[secret_name] = secret
      self.timestamps[secret_name] = current_time
      return secret
    except ClientError as e:
      raise Exception(f"Error fetching secret {secret_name}: {e}")