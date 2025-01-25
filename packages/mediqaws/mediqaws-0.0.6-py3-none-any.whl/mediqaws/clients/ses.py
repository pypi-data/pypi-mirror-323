from .abc import AwsClient

class Ses(AwsClient):
  @property
  def service_name(self) -> str:
    return "ses"
  
  def send_raw_email(
    self,
    raw_message: bytes
  ) -> dict:
    """
    Send an email using SES.
    
    Args:
      raw_message: The raw email message to send.
    
    Returns:
      The response from SES.
    """
    return self.client.send_raw_email(
      RawMessage={"Data": raw_message}
    )