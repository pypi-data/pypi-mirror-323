def get_presigned_url(s3Client, bucket_name, object_key, expiration=3600):
    """Generate a presigned URL to share an S3 object."""
    s3 = s3Client
    try:
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name, 'Key': object_key},
                                        ExpiresIn=expiration)
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None