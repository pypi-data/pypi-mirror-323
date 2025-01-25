# mediqaws

A collection of AWS clients, and asecrets manager.

## Install

`pip install mediqaws`

## Usage

```python
from mediqaws.clients import S3

profile_name = "..."
bucket_name = "..."
object_key_prefix = "..."
file_path = "..."

with S3(profile_name=profile_name) as s3:
  object_key = s3.upload(file_path, bucket_name, object_key_prefix)
print(object_key)
```

```python
from mediqaws.secrets_manager import SecretsManager

secrets_manager = SecretsManager()
secret = secrets_manager.get_secret(os.getenv("SECRET_NAME"))
print(secret)
```

See more examples under `tests` directory.
