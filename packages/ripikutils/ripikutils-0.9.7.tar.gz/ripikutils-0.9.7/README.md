# ripikutils

`ripikutils` is a Python package designed to provide utility functions for MongoDB operations and AWS S3 interactions, specifically tailored for internal use at Ripik Tech.

[![PyPI version](https://badge.fury.io/py/ripikutils.svg)](https://badge.fury.io/py/ripikutils)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [Creation of Secret Manager](#creation-of-secret-manager)
- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
  - [MongoDB Operations](#mongodb-operations)
  - [AWS s3 Operations](#aws-s3-operations)
- [License](#license)
- [Contact](#contact)

## Creation of Secret Manager

Every secret manager added should follow these guidelines:
- Format: `ripikutils/{clientName}/{useCase}`
- Data added inside the secret should at least include the following values:
  - `mongoURI`
  - `dbName`
  - `useCase`
  - `s3Bucket`

## Installation

You can install `ripikutils` using pip:

```
pip install ripikutils
```


## Features

- MongoDB data filtering, insertion, updating, and deletion
- AWS S3 operations (upload, download, delete, list)
- Temporary directory management for image processing

## Usage

### MongoDB Operations

#### Initialize Mongo Client
Initialize MongoDB client using client name and its usecase
```python
from ripikutils import initialize_mongo

mongo_client = initialize_mongo(client_name, usecase)
```

#### Apply Filter
Apply basic filter to your MongoDB query
```python

filtered_data = mongo_client.apply_filter(collection, filter_params)
```

#### Insert Document
Insert documents to your MongoDB collection
```python

mongo_client.insert(collection, document)
```

#### Update Document
Update a document in your MongoDB collection
```python

mongo_client.update(collection, filter_params, update_params)
```

#### Delete Document
Delete a document from your MongoDB collection
```python

mongo_client.delete(collection, filter_params)
```

### AWS S3 Operations

#### Initialize AWS s3 Client
Initialize S3 Client using client name and usecase
```python
from ripikutils import initialize_s3

s3_client = initialize_s3(client_name, usecase)
```

#### Upload Object/File
Upload a file to S3 using previously created `s3_client`
```python

s3_client.upload_s3_object(file_path, object_name)
```

#### Download Object/File
Download a file from S3 using previously created `s3_client`
```python

s3_client.download_s3_object(object_name, local_file_path)
```

#### Delete Object/File
Delete a file from S3 using previously created `s3_client`
```python

s3_client.delete_s3_object(bucket_name, object_name)
```

#### Get Presigned URL
Get a presigned URL for a file in S3 using previously created `s3_client`
```python

presigned_url = s3_client.get_presigned_url(object_name)
```

#### List Objects in S3 Bucket
List objects in a S3 bucket using previously created `s3_client`
```python

objects = s3_client.list_s3_objects()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any queries or support, please contact the Ripik Tech team at [vaibhav@ripik.ai](mailto:vaibhav@ripik.ai).