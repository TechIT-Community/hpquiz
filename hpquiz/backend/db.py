from typing import Any, Callable, Literal, Union

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.client_session import ClientSession



class Database:
    """
    A class to represent a MongoDB database connection and operations.
    Attributes:
    -----------
    client : MongoClient
        The MongoDB client instance.
    db : Database
        The MongoDB database instance.
    Methods:
    --------
    get_collection(name: str) -> Collection:
        Returns the collection with the given name.
    execute_with_session(operations: Callable[[ClientSession], Any]) -> Any:
        Executes the given operations within a session and transaction.
    insert_one(collection_name: str, data: Any) -> InsertOneResult:
        Inserts a single document into the specified collection.
    find_one(collection_name: str, query: dict) -> Optional[dict]:
        Finds a single document in the specified collection that matches the query.
    update_one(collection_name: str, query: dict, update: dict) -> UpdateResult:
        Updates a single document in the specified collection that matches the query.
    delete_one(collection_name: str, query: dict) -> DeleteResult:
        Deletes a single document in the specified collection that matches the query.
    """
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, name: str):
        """
        Retrieve a collection from the database by name.
        Args:
            name (str): The name of the collection to retrieve.
        Returns:
            Collection: The collection object corresponding to the given name.
        """
        
        return self.db[name]

    def execute_with_session(self, operations: Callable[[ClientSession], Any]):
        """
        Executes a series of database operations within a session and transaction.
        This method starts a new client session and transaction, then executes the
        provided operations within that context. The operations should be a callable
        that accepts a ClientSession object and performs the necessary database actions.
        Args:
            operations (Callable[[ClientSession], Any]): A callable that takes a 
            ClientSession as an argument and performs database operations.
        Returns:
            Any: The result of the operations callable.
        """
        
        with self.client.start_session() as session:
            with session.start_transaction():
                return operations(session)

    def insert_one(self, collection_name: str, data: Any):
        """
        Inserts a single document into the specified collection.
        Args:
            collection_name (str): The name of the collection where the document will be inserted.
            data (Any): The document to be inserted.
        Returns:
            InsertOneResult: The result of the insert operation.
        Raises:
            Exception: If the insert operation fails.
        """
        
        return self.execute_with_session(lambda session: self.get_collection(collection_name).insert_one(data, session=session))

    def find_one(self, collection_name: str, query: dict):
        """
        Find a single document in the specified collection that matches the query.
        Args:
            collection_name (str): The name of the collection to search in.
            query (dict): The query criteria to match documents against.
        Returns:
            dict: The first document that matches the query criteria, or None if no document matches.
        """
        
        return self.execute_with_session(lambda session: self.get_collection(collection_name).find_one(query, session=session))

    def update_one(self, collection_name: str, query: dict, update: dict):
        """
        Update a single document in the specified collection.
        Args:
            collection_name (str): The name of the collection to update.
            query (dict): The query to match the document to update.
            update (dict): The update operations to apply to the matched document.
        Returns:
            pymongo.results.UpdateResult: The result of the update operation.
        """
        
        return self.execute_with_session(lambda session: self.get_collection(collection_name).update_one(query, update, session=session))

    def delete_one(self, collection_name: str, query: dict):
        """
        Deletes a single document from the specified collection that matches the given query.
        Args:
            collection_name (str): The name of the collection from which to delete the document.
            query (dict): The query used to match the document to be deleted.
        Returns:
            pymongo.results.DeleteResult: The result of the delete operation.
        """
        
        return self.execute_with_session(lambda session: self.get_collection(collection_name).delete_one(query, session=session))
    
    def find(self, collection_name: str, query: dict, sort_key: str = None, order: Union[Literal[1], Literal[-1]] = ASCENDING):
        """
        Finds documents in a specified collection based on a query.
        Args:
            collection_name (str): The name of the collection to search in.
            query (dict): The query to filter documents.
            sort_key (str, optional): The key to sort the results by. Defaults to None.
            order (Union[Literal[1], Literal[-1]], optional): The order of sorting, either ascending (1) or descending (-1). Defaults to ASCENDING[1].
        Returns:
            list: A list of documents that match the query.
        """
        
        def find_operation(session):
            cursor = self.get_collection(collection_name).find(query, session=session)
            if sort_key:
                cursor = cursor.sort(sort_key)
            return cursor
            
        return list(self.execute_with_session(find_operation))
    
    def insert_many(self, collection_name: str, data: list[Any]):
        """
        Inserts multiple documents into the specified collection.

        Args:
            collection_name (str): The name of the collection where the documents will be inserted.
            data (List[Any]): The list of documents to be inserted.

        Returns:
            InsertManyResult: The result of the insert operation.

        Raises:
            Exception: If the insert operation fails.
        """
        return self.execute_with_session(
            lambda session: self.get_collection(collection_name).insert_many(data, session=session)
        )