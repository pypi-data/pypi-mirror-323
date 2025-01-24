from ..secrets.secrets_manager import get_secret

import pymongo, certifi

class MongoClient:
    def __init__(self, client_name: str, usecase: str = None):
        self.client_name = client_name
        self.usecase = usecase
        self.mongo_client, self.dbName = self._get_mongo_client()

    def _get_mongo_client(self):
        secret_var = f"ripikutils/{self.client_name}/{self.usecase}"
        secrets = get_secret(secret_var)
        return (pymongo.MongoClient(secrets['mongoURI'], tlsCAFile=certifi.where()), secrets["dbName"])

    def get_collection(self, collection_name: str):
        client_db = self.mongo_client[self.dbName]
        client_collection = client_db[collection_name]
        return client_collection

    def delete(self, collection_name: str, filter_query, many: bool = False):
        collection = self.get_collection(collection_name)
        try:
            if many:
                result = collection.delete_many(filter_query)
            else:
                result = collection.delete_one(filter_query)
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting document: {e}")
            return 0

    def filter(self, collection_name: str, filter_query):
        collection = self.get_collection(collection_name)
        try:
            results = collection.find(filter_query)
            return list(results)
        except Exception as e:
            print(f"Error applying filter: {e}")
            return []

    def insert(self, collection_name: str, document):
        collection = self.get_collection(collection_name)
        try:
            result = collection.insert_one(document)
            return f"Inserted document with _id: {result.inserted_id}"
        except Exception as e:
            print(f"Error inserting document: {e}")

    def update(self, collection_name: str, filter_query, update_data):
        collection = self.get_collection(collection_name)
        try:
            result = collection.update_one(filter_query, {'$set': update_data})
            return f"Updated {result.modified_count} document(s) matching {filter_query}"
        except Exception as e:
            print(f"Error updating document: {e}")
            
            
def initialize_mongo(client_name: str, usecase: str = None):
    return MongoClient(client_name, usecase)
