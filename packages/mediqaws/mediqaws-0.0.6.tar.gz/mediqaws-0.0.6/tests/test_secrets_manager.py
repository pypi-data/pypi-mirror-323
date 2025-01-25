import os

from mediqaws.secrets_manager import SecretsManager

def test_get_secret():
  secrets_manager = SecretsManager()
  secret = secrets_manager.get_secret(os.getenv("SECRET_NAME"))
  print(secret)
  assert secret is not None and len(secret) > 0