def list_s3_objects(s3Client, bucket_name, prefix=None):
    """List objects in an S3 bucket."""
    s3 = s3Client
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = [obj['Key'] for obj in response.get('Contents', [])]
        return objects
    except Exception as e:
        print(f"Error listing objects in {bucket_name}: {e}")
        return []