def apply_filter(mongo_client, database_name, collection_name, filter_query):
    """Filter documents in a MongoDB collection."""
    return mongo_client.filter(database_name, collection_name, filter_query)