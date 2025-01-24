def delete_s3_object(s3Client, bucket_name, object_key):
    """
    The function `delete_s3_object` deletes an object from an S3 bucket using the provided S3 client,
    bucket name, and object key.
    
    :param s3Client: The `s3Client` parameter is typically an instance of the AWS SDK for Python (Boto3)
    `s3` client that is used to interact with Amazon S3 services. This client provides methods for
    performing operations on S3 buckets and objects, such as uploading, downloading, and deleting
    :param bucket_name: The `bucket_name` parameter in the `delete_s3_object` function refers to the
    name of the Amazon S3 bucket from which you want to delete an object. This is the bucket where the
    object with the specified `object_key` exists and needs to be deleted
    :param object_key: The `object_key` parameter in the `delete_s3_object` function represents the
    unique identifier of the object you want to delete from the specified S3 bucket. It is the key that
    uniquely identifies the object within the bucket. For example, if you have an object with the key
    "example.txt
    """

    s3 = s3Client
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"Deleted {object_key} from {bucket_name}")
    except Exception as e:
        print(f"Error deleting {object_key} from {bucket_name}: {e}")


def bulk_s3_delete(s3Client, file_list, bucket_name, custom_object_paths):
    """
    The function `bulk_s3_delete` deletes multiple files from an S3 bucket using custom object paths.
    
    :param s3Client: The `s3Client` parameter is typically an instance of an AWS SDK client that allows
    you to interact with Amazon S3 services. It provides methods for performing operations such as
    uploading, downloading, and deleting objects in S3 buckets
    :param file_list: A list of file names that you want to delete from the S3 bucket
    :param bucket_name: The `bucket_name` parameter in the `bulk_s3_delete` function is a string that
    represents the name of the Amazon S3 bucket from which the files will be deleted. This bucket should
    already exist in your AWS account and the provided `s3Client` should have the necessary permissions
    to access
    :param custom_object_paths: Custom object paths are user-defined paths or keys that specify the
    location of objects within an S3 bucket. These paths can be used to organize and categorize objects
    within the bucket. In the context of the `bulk_s3_delete` function, `custom_object_paths` is a list
    of custom paths
    """

    assert len(file_list) > 0, "No files to delete"
    assert len(file_list) == len(custom_object_paths), "Number of files and custom object paths on the bucket do not match"

    for file, custom_path in zip(file_list, custom_object_paths):
        delete_s3_object(s3Client, file, bucket_name, custom_path)