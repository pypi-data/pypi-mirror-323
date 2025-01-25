from pydantic import BaseModel
from typing import Optional

from .abc import AwsClient

class SnsPublishArgs(BaseModel):
  # See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/publish.html
  Subject: Optional[str] = None
  MessageAttributes: Optional[dict] = None
  MessageDuplicationId: Optional[str] = None
  MessageGroupId: Optional[str] = None
  
class Sns(AwsClient):
  @property
  def service_name(self) -> str:
    return "sns"
  
  def publish(
    self,
    topic_arn: str,
    message: str,
    args: SnsPublishArgs,
    **kwargs
  ) -> dict:
    """
    Publish a message to an SNS topic.
    
    Args:
      topic_arn: The ARN of the topic to publish to.
      message: The message to publish.
      args: Additional arguments for the publish operation.
    
    Returns:
      The response from SNS.
    """
    return self.client.publish(
      TopicArn=topic_arn,
      Message=message,
      **args.model_dump(mode="json", exclude_none=True, exclude_unset=True),
      **kwargs
    )