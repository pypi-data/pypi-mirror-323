def insert_document(mongo_client, database_name, collection_name, document):
    """Insert a document into a MongoDB collection."""
    mongo_client.insert(database_name, collection_name, document)