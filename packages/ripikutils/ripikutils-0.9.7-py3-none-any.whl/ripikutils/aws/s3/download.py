def download_s3_object(s3Client, bucket_name, object_key, download_path):
    """
    The function `download_s3_object` downloads an object from an S3 bucket using the provided client,
    bucket name, object key, and saves it to a specified download path.
    
    :param s3Client: The `s3Client` parameter in the `download_s3_object` function is typically an
    instance of an AWS SDK client for interacting with Amazon S3, such as `boto3.client('s3')` in
    Python. This client is used to make requests to the Amazon S3 service
    :param bucket_name: The `bucket_name` parameter in the `download_s3_object` function refers to the
    name of the Amazon S3 bucket from which you want to download an object. Amazon S3 is a cloud storage
    service provided by Amazon Web Services (AWS), and buckets are containers for storing objects
    (files)
    :param object_key: The `object_key` parameter in the `download_s3_object` function refers to the
    unique identifier or name of the object you want to download from the specified S3 bucket. It is
    used to locate the specific object within the bucket for downloading
    :param download_path: The `download_path` parameter in the `download_s3_object` function represents
    the local file path where the downloaded object from the S3 bucket will be saved. This is the
    location on your local machine where the file will be stored after downloading it from the specified
    S3 bucket
    """
    
    s3 = s3Client
    try:
        s3.download_file(bucket_name, object_key, download_path)
        print(f"Downloaded {object_key} from {bucket_name} to {download_path}")
    except Exception as e:
        print(f"Error downloading {object_key}: {e}")


def bulk_s3_download(s3Client, bucket_name, custom_object_paths, download_paths):
    """
    The function `bulk_s3_download` downloads multiple objects from an S3 bucket to specified local
    paths.
    
    :param s3Client: The `s3Client` parameter is the client object that allows you to interact with
    Amazon S3 service. It is typically an instance of the `boto3.client('s3')` class in Python, which
    provides methods for interacting with Amazon S3 buckets and objects
    :param bucket_name: The `bucket_name` parameter in the `bulk_s3_download` function is the name of
    the Amazon S3 bucket from which you want to download the files. This bucket should already exist in
    your AWS account and should contain the files that you want to download
    :param custom_object_paths: Custom object paths are the paths of the objects in the S3 bucket that
    you want to download. These paths are specific to the objects within the bucket and are used to
    identify the objects that you want to download
    :param download_paths: The `download_paths` parameter in the `bulk_s3_download` function is a list
    of local file paths where the downloaded objects from the S3 bucket will be saved. Each element in
    the `download_paths` list corresponds to the custom object path in the S3 bucket specified in the
    `custom
    """
    
    assert len(custom_object_paths) > 0, "No files to upload"
    assert len(custom_object_paths) == len(download_paths), "Number of files and custom object paths on the bucket do not match"

    for custom_path, download_path in zip(custom_object_paths, download_paths):
        download_s3_object(s3Client, bucket_name, custom_path, download_path)