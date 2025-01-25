import boto3

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, PrivateAttr
from typing import Any
from typing_extensions import Self

class AwsClient(BaseModel, ABC):
  profile_name: str = Field(..., description="The AWS profile name")
  
  _client: Any = PrivateAttr(None)
  
  @property
  def client(self):
    return self._client
  
  @property
  @abstractmethod
  def service_name(self) -> str:
    """
    The name of the AWS service, e.g. "s3", "kms", etc.
    """
    pass
  
  def __enter__(self) -> Self:
    session = boto3.Session(profile_name=self.profile_name)
    self._client = session.client(self.service_name)
    return self
  
  def __exit__(self, *_):
    self._client = None