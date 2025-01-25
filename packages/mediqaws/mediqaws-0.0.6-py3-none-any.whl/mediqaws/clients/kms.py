from .abc import AwsClient

class Kms(AwsClient):
  @property
  def service_name(self) -> str:
    return "kms"
  
  def decrypt(
    self,
    blob: bytes,
    **kwargs
  ) -> dict:
    """
    Decrypt data using a KMS key.
    
    Args:
      blob: The data to decrypt.
    
    Returns:
      The decrypted result.
    """
    return self.client.decrypt(
      CiphertextBlob=blob, **kwargs
    )