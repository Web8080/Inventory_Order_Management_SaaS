"""
MongoDB Client for ML Data Storage and Retrieval
Provides efficient data access for ML pipeline
"""

import pymongo
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime
import pandas as pd


class MongoClient:
    """
    MongoDB client for ML data operations
    Handles data storage, retrieval, and caching for ML pipeline
    """
    
    def __init__(self, connection_string: str = None, database_name: str = "inventory_ml"):
        """
        Initialize MongoDB client
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name for ML data
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self.client is not None and self.db is not None
    
    def store_training_data(self, tenant_id: str, data: pd.DataFrame, 
                           metadata: Dict[str, Any] = None) -> str:
        """
        Store training data in MongoDB
        
        Args:
            tenant_id: Tenant identifier
            data: Training data DataFrame
            metadata: Additional metadata
            
        Returns:
            Document ID of stored data
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return None
        
        try:
            collection = self.db['training_data']
            
            # Convert DataFrame to records
            records = data.to_dict('records')
            
            # Prepare document
            document = {
                'tenant_id': tenant_id,
                'data': records,
                'metadata': metadata or {},
                'created_at': datetime.now(),
                'record_count': len(records),
                'columns': list(data.columns)
            }
            
            # Insert document
            result = collection.insert_one(document)
            print(f"Stored training data for tenant {tenant_id}: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error storing training data: {e}")
            return None
    
    def get_training_data(self, tenant_id: str, limit: int = None) -> pd.DataFrame:
        """
        Retrieve training data from MongoDB
        
        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of records to retrieve
            
        Returns:
            Training data DataFrame
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return pd.DataFrame()
        
        try:
            collection = self.db['training_data']
            
            # Query for tenant data
            query = {'tenant_id': tenant_id}
            cursor = collection.find(query).sort('created_at', -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            # Get most recent data
            document = cursor.next()
            
            if not document:
                print(f"No training data found for tenant {tenant_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = pd.DataFrame(document['data'])
            
            print(f"Retrieved training data for tenant {tenant_id}: {len(data)} records")
            return data
            
        except Exception as e:
            print(f"Error retrieving training data: {e}")
            return pd.DataFrame()
    
    def store_model_metrics(self, tenant_id: str, model_name: str, 
                           metrics: Dict[str, Any], model_data: Dict[str, Any] = None) -> str:
        """
        Store model metrics and performance data
        
        Args:
            tenant_id: Tenant identifier
            model_name: Name of the model
            metrics: Model performance metrics
            model_data: Additional model data
            
        Returns:
            Document ID of stored metrics
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return None
        
        try:
            collection = self.db['model_metrics']
            
            document = {
                'tenant_id': tenant_id,
                'model_name': model_name,
                'metrics': metrics,
                'model_data': model_data or {},
                'created_at': datetime.now(),
                'version': metrics.get('version', '1.0')
            }
            
            result = collection.insert_one(document)
            print(f"Stored model metrics for {model_name}: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error storing model metrics: {e}")
            return None
    
    def get_model_metrics(self, tenant_id: str, model_name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve model metrics from MongoDB
        
        Args:
            tenant_id: Tenant identifier
            model_name: Specific model name (optional)
            
        Returns:
            List of model metrics
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return []
        
        try:
            collection = self.db['model_metrics']
            
            query = {'tenant_id': tenant_id}
            if model_name:
                query['model_name'] = model_name
            
            cursor = collection.find(query).sort('created_at', -1)
            metrics = list(cursor)
            
            print(f"Retrieved {len(metrics)} model metrics for tenant {tenant_id}")
            return metrics
            
        except Exception as e:
            print(f"Error retrieving model metrics: {e}")
            return []
    
    def store_predictions(self, tenant_id: str, predictions: List[Dict[str, Any]], 
                         model_name: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store model predictions
        
        Args:
            tenant_id: Tenant identifier
            predictions: List of predictions
            model_name: Name of the model
            metadata: Additional metadata
            
        Returns:
            Document ID of stored predictions
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return None
        
        try:
            collection = self.db['predictions']
            
            document = {
                'tenant_id': tenant_id,
                'model_name': model_name,
                'predictions': predictions,
                'metadata': metadata or {},
                'created_at': datetime.now(),
                'prediction_count': len(predictions)
            }
            
            result = collection.insert_one(document)
            print(f"Stored predictions for {model_name}: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error storing predictions: {e}")
            return None
    
    def get_predictions(self, tenant_id: str, model_name: str = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve model predictions
        
        Args:
            tenant_id: Tenant identifier
            model_name: Specific model name (optional)
            limit: Maximum number of predictions to retrieve
            
        Returns:
            List of predictions
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return []
        
        try:
            collection = self.db['predictions']
            
            query = {'tenant_id': tenant_id}
            if model_name:
                query['model_name'] = model_name
            
            cursor = collection.find(query).sort('created_at', -1).limit(limit)
            predictions = list(cursor)
            
            print(f"Retrieved {len(predictions)} predictions for tenant {tenant_id}")
            return predictions
            
        except Exception as e:
            print(f"Error retrieving predictions: {e}")
            return []
    
    def store_feature_importance(self, tenant_id: str, model_name: str, 
                                feature_importance: Dict[str, float]) -> str:
        """
        Store feature importance data
        
        Args:
            tenant_id: Tenant identifier
            model_name: Name of the model
            feature_importance: Feature importance scores
            
        Returns:
            Document ID of stored feature importance
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return None
        
        try:
            collection = self.db['feature_importance']
            
            document = {
                'tenant_id': tenant_id,
                'model_name': model_name,
                'feature_importance': feature_importance,
                'created_at': datetime.now()
            }
            
            result = collection.insert_one(document)
            print(f"Stored feature importance for {model_name}: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error storing feature importance: {e}")
            return None
    
    def get_feature_importance(self, tenant_id: str, model_name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve feature importance data
        
        Args:
            tenant_id: Tenant identifier
            model_name: Specific model name (optional)
            
        Returns:
            List of feature importance data
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return []
        
        try:
            collection = self.db['feature_importance']
            
            query = {'tenant_id': tenant_id}
            if model_name:
                query['model_name'] = model_name
            
            cursor = collection.find(query).sort('created_at', -1)
            feature_importance = list(cursor)
            
            print(f"Retrieved {len(feature_importance)} feature importance records for tenant {tenant_id}")
            return feature_importance
            
        except Exception as e:
            print(f"Error retrieving feature importance: {e}")
            return []
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        if not self.is_connected():
            print("MongoDB not connected")
            return
        
        try:
            # Training data indexes
            self.db['training_data'].create_index([('tenant_id', 1), ('created_at', -1)])
            
            # Model metrics indexes
            self.db['model_metrics'].create_index([('tenant_id', 1), ('model_name', 1), ('created_at', -1)])
            
            # Predictions indexes
            self.db['predictions'].create_index([('tenant_id', 1), ('model_name', 1), ('created_at', -1)])
            
            # Feature importance indexes
            self.db['feature_importance'].create_index([('tenant_id', 1), ('model_name', 1), ('created_at', -1)])
            
            print("Database indexes created successfully")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    def cleanup_old_data(self, days: int = 90):
        """
        Clean up old data to manage storage
        
        Args:
            days: Number of days to keep data
        """
        if not self.is_connected():
            print("MongoDB not connected")
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean up old training data
            result1 = self.db['training_data'].delete_many({'created_at': {'$lt': cutoff_date}})
            print(f"Deleted {result1.deleted_count} old training data records")
            
            # Clean up old predictions
            result2 = self.db['predictions'].delete_many({'created_at': {'$lt': cutoff_date}})
            print(f"Deleted {result2.deleted_count} old prediction records")
            
            # Keep model metrics and feature importance (they're smaller)
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.is_connected():
            return {'error': 'MongoDB not connected'}
        
        try:
            stats = {
                'database_name': self.database_name,
                'collections': {},
                'total_size': 0
            }
            
            # Get collection stats
            for collection_name in ['training_data', 'model_metrics', 'predictions', 'feature_importance']:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                stats['collections'][collection_name] = {
                    'document_count': count,
                    'size_mb': collection.estimated_document_count() * 0.001  # Rough estimate
                }
                stats['total_size'] += stats['collections'][collection_name]['size_mb']
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")


# Global MongoDB client instance
_mongo_client = None

def get_mongo_client() -> MongoClient:
    """Get global MongoDB client instance"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient()
    return _mongo_client

def close_mongo_client():
    """Close global MongoDB client"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
