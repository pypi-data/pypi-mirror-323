from pydantic import BaseModel, Field
from typing import Optional

from .abc import AwsClient

class SqsReceiveArgs(BaseModel):
  # See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/client/receive_message.html
  MaxNumberOfMessages: Optional[int] = Field(1, gt=1, le=10)
  VisibilityTimeout: Optional[int] = None
  WaitTimeSeconds: Optional[int] = None

class Sqs(AwsClient):
  @property
  def service_name(self) -> str:
    return "sqs"
  
  def receive(
    self,
    queue_url: str,
    args: SqsReceiveArgs,
    **kwargs
  ) -> list[dict]:
    """
    Receive messages from an SQS queue.
    
    Args:
      queue_url: The URL of the queue to receive messages from.
      args: Additional arguments for the receive operation.
    
    Returns:
      The response from SQS.
    """
    return self.client.receive_message(
      QueueUrl=queue_url,
      **args.model_dump(mode="json", exclude_none=True, exclude_unset=True),
      **kwargs
    )
  
  def delete_messages(
    self,
    queue_url: str,
    messages: list[dict]
  ) -> dict:
    """
    Delete messages from an SQS queue.
    
    Args:
      queue_url: The URL of the queue containing the messages.
      messages: The messages to delete.
    
    Returns:
      The response from SQS. See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/client/delete_message_batch.html
    """
    remained = [] + messages # Make a copy of messages
    result = {
      "Successful": [],
      "Failed": [],
    }
    
    while remained:
      candidates = remained[:10]
      remained = remained[10:]
      
      batch = []
      ids = set()
      
      for msg in candidates:
        if msg["MessageId"][:80] in ids:
          remained.append(msg)
          continue
        batch.append({
          "Id": msg["MessageId"][:80],
          "ReceiptHandle": msg["ReceiptHandle"],
        })
        ids.add(msg["MessageId"][:80])
        
      response = self.client.delete_message_batch(
        QueueUrl=queue_url,
        Entries=batch
      )
      result["Successful"] += response.get("Successful", [])
      result["Failed"] += response.get("Failed", [])
      
    return result
  
  def change_message_visibility_batch(
    self,
    queue_url: str,
    messages: list[dict],
    visibility_timeout: int
  ) -> dict:
    """
    Change the visibility timeout of messages in an SQS queue.
    
    Args:
      queue_url: The URL of the queue containing the messages.
      messages: The messages to change the visibility timeout of.
      visibility_timeout: The new visibility timeout for the messages.
    
    Returns:
      The response from SQS. See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/client/change_message_visibility_batch.html
    """
    entries = [{
      "Id": msg["MessageId"],
      "ReceiptHandle": msg["ReceiptHandle"],
      "VisibilityTimeout": visibility_timeout
    } for msg in messages]
    
    return self.client.change_message_visibility_batch(
      QueueUrl=queue_url,
      Entries=entries
    )