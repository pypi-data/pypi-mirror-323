from ...secrets.secrets_manager import get_secret
import boto3

class S3Client:
    def __init__(self, client_name: str, usecase: str = None):
        self.client_name = client_name
        self.usecase = usecase
        self.secret = get_secret(f"ripikutils/{self.client_name}/{self.usecase}")
        self.s3Bucket = self.secret["s3Bucket"]
        self.s3 = boto3.client('s3')

    def upload_object(self, file_path, object_key):
        """Upload a file to S3."""
        try:
            self.s3.upload_file(file_path, self.s3Bucket, object_key)
            print(f"Uploaded {file_path} to {self.s3Bucket}/{object_key}")
        except Exception as e:
            print(f"Error uploading {file_path} to S3: {e}")

    def download_object(self, object_key, download_path):
        """Download an object from S3 to a local path."""
        try:
            self.s3.download_file(self.s3Bucket, object_key, download_path)
            print(f"Downloaded {object_key} from {self.s3Bucket} to {download_path}")
        except Exception as e:
            print(f"Error downloading {object_key}: {e}")

    def delete_object(self, object_key):
        """Delete an object from S3."""
        try:
            self.s3.delete_object(Bucket=self.s3Bucket, Key=object_key)
            print(f"Deleted {object_key} from {self.s3Bucket}")
        except Exception as e:
            print(f"Error deleting {object_key} from {self.s3Bucket}: {e}")

    def list_objects(self, prefix=None):
        """List objects in an S3 bucket."""
        try:
            response = self.s3.list_objects_v2(Bucket=self.s3Bucket, Prefix=prefix)
            objects = [obj['Key'] for obj in response.get('Contents', [])]
            return objects
        except Exception as e:
            print(f"Error listing objects in {self.s3Bucket}: {e}")
            return []

    def get_presigned_url(self, object_key, expiration=3600):
        """Generate a presigned URL to share an S3 object."""
        try:
            url = self.s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': self.s3Bucket, 'Key': object_key},
                                                  ExpiresIn=expiration)
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

def initialize_s3(client_name: str, usecase: str = None):
    return S3Client(client_name, usecase)

def get_vanilla_s3_client():
    return boto3.client('s3')