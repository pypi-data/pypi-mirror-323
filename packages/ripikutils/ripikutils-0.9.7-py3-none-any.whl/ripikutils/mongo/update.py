def update_document(mongo_client, database_name, collection_name, filter_query, update_data):
    """Update a document in a MongoDB collection."""
    mongo_client.update(database_name, collection_name, filter_query, update_data)