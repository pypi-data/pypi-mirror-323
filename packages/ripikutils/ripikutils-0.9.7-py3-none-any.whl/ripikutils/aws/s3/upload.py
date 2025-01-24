def upload_s3_object(s3Client, file_path, bucket_name, object_key):
    """
    The function `upload_s3_object` uploads a file to an S3 bucket using the provided S3 client, file
    path, bucket name, and object key.
    
    :param s3Client: The `s3Client` parameter in the `upload_s3_object` function is typically an
    instance of an AWS SDK client for interacting with Amazon S3, such as `boto3.client('s3')` in
    Python. This client is used to make API calls to Amazon S3 for
    :param file_path: The `file_path` parameter in the `upload_s3_object` function represents the local
    file path of the file that you want to upload to an Amazon S3 bucket. This is the location on your
    local machine where the file is stored before being uploaded to the specified S3 bucket
    :param bucket_name: The `bucket_name` parameter in the `upload_s3_object` function refers to the
    name of the Amazon S3 bucket where you want to upload the file specified by `file_path` with the
    object key `object_key`. This bucket acts as a container for storing objects (files) in Amazon
    :param object_key: The `object_key` parameter in the `upload_s3_object` function represents the
    unique identifier or name that you want to assign to the object being uploaded to the S3 bucket. It
    is used to specify the key under which the uploaded file will be stored in the S3 bucket
    """
    
    s3 = s3Client
    try:
        s3.upload_file(file_path, bucket_name, object_key)
        print(f"Uploaded {file_path} to {bucket_name}/{object_key}")
    except Exception as e:
        print(f"Error uploading {file_path} to S3: {e}")

def bulk_s3_upload(s3Client, file_list, bucket_name, custom_object_paths):
    """
    The function `bulk_s3_upload` uploads a list of files to an S3 bucket with custom object paths.
    
    :param s3Client: The `s3Client` parameter is typically an instance of an AWS SDK client that allows
    you to interact with Amazon S3 services. This client provides methods for uploading files to S3
    buckets, managing objects, and performing other operations related to S3 storage. You can create an
    instance of the client
    :param file_list: A list of file paths that you want to upload to an S3 bucket
    :param bucket_name: The `bucket_name` parameter in the `bulk_s3_upload` function is the name of the
    Amazon S3 bucket where the files will be uploaded. This is the destination bucket where the files
    from the `file_list` will be uploaded to
    :param custom_object_paths: The `custom_object_paths` parameter in the `bulk_s3_upload` function is
    a list that contains custom object paths for each file in the `file_list`. The function will upload
    each file to the specified `bucket_name` with the corresponding custom object path from the
    `custom_object_paths` list
    """
    

    assert len(file_list) > 0, "No files to upload"
    assert len(file_list) == len(custom_object_paths), "Number of files and custom object paths on the bucket do not match"

    for file, custom_path in zip(file_list, custom_object_paths):
        upload_s3_object(s3Client, file, bucket_name, custom_path)