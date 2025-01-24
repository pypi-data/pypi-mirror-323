from .mongo import initialize_mongo
from .mongo import example_usage as example_usage_mongo
from .mongo import delete as mongo_delete
from .mongo import filter, insert, update
from .aws.s3 import initialize_s3
from .aws.s3 import delete as aws_s3_delete
from .aws.s3 import download, get_presigned_url, list, upload
from .aws.s3 import example_usage as example_usage_s3

__all__ = [
    'aws',
    'mongo',
    'initialize_mongo',
    'initialize_s3',
    'example_usage_mongo',
    'example_usage_s3',
    '__version__'
]

__version__ = "0.9.0"


class aws:
    initalize = initialize_s3
    check_aws_s3 = example_usage_s3.check
    delete = aws_s3_delete.delete_s3_object
    download = download.download_s3_object
    get_presigned_url = get_presigned_url.get_presigned_url
    list = list.list_s3_objects
    upload = upload.upload_s3_object
    
class mongo:
    initialize = initialize_mongo
    check_mongo = example_usage_mongo.check
    delete = mongo_delete.delete_document
    filter = filter.apply_filter
    insert = insert.insert_document
    update = update.update_document