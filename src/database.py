"""
Database connection and management module
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import hashlib
from config import Config


class Database:
    """Database connection handler with connection pooling"""
    
    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 20,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self, user: str = None, password: str = None):
        """
        Get a connection from the pool or create a new one with specific credentials
        
        Args:
            user: Database user (if None, uses default from config)
            password: Database password (if None, uses default from config)
        
        Returns:
            Database connection
        """
        if user and password:
            # Create new connection with specific user credentials
            return psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=user,
                password=password
            )
        else:
            # Use connection pool
            return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
    
    def execute_query(
        self, 
        query: str, 
        params: tuple = None,
        user: str = None,
        password: str = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            user: Database user (optional)
            password: Database password (optional)
            fetch: Whether to fetch results
        
        Returns:
            List of dictionaries representing rows, or None
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection(user, password)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                conn.commit()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return None
                
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Query execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                if user and password:
                    conn.close()
                else:
                    self.return_connection(conn)
    
    def get_table_data(
        self, 
        table_name: str, 
        user: str = None, 
        password: str = None
    ) -> List[Dict[str, Any]]:
        """Get all data from a table"""
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query, user=user, password=password)
    
    def log_query_audit(
        self,
        username: str,
        query_text: str,
        result_count: int = 0,
        was_blocked: bool = False,
        block_reason: str = None
    ):
        """Log query to audit table"""
        audit_query = """
            INSERT INTO query_audit (username, query_text, result_count, was_blocked, block_reason)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_query(
            audit_query,
            (username, query_text, result_count, was_blocked, block_reason),
            fetch=False
        )
    
    def store_query_history(
        self,
        username: str,
        query_text: str,
        result_set: List[Dict[str, Any]] = None
    ):
        """Store query in history for overlap detection"""
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()
        
        # Calculate result set hash if provided
        result_hash = None
        if result_set:
            result_str = str(sorted([str(sorted(r.items())) for r in result_set]))
            result_hash = hashlib.sha256(result_str.encode()).hexdigest()
        
        history_query = """
            INSERT INTO query_history (username, query_hash, query_text, result_set_hash)
            VALUES (%s, %s, %s, %s)
        """
        self.execute_query(
            history_query,
            (username, query_hash, query_text, result_hash),
            fetch=False
        )
    
    def get_query_history(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history for a user"""
        query = """
            SELECT * FROM query_history
            WHERE username = %s
            ORDER BY execution_time DESC
            LIMIT %s
        """
        return self.execute_query(query, (username, limit))
    
    def set_user_clearance(self, clearance_level: int, user: str = None, password: str = None):
        """Set user clearance level for polyinstantiation"""
        query = f"SET app.user_clearance = {clearance_level}"
        self.execute_query(query, user=user, password=password, fetch=False)


# Global database instance
db = Database()