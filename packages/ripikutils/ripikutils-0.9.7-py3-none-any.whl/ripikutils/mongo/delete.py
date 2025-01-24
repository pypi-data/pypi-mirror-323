def delete_document(mongo_client, database_name, collection_name, filter_query):
    """Delete a document from MongoDB collection."""
    return mongo_client.delete(database_name, collection_name, filter_query)