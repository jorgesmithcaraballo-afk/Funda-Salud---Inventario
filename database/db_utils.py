"""
Database utilities with proper context managers and error handling
Ensures connections are always properly closed
"""
import mysql.connector
from typing import Any, Dict, Generator, Optional, List
from contextlib import contextmanager
import logging
from config import db_config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


class ConnectionManager:
    """Database connection manager with proper resource handling"""
    
    @staticmethod
    @contextmanager
    def get_connection(config: Optional[Dict[str, Any]] = None) -> Generator[mysql.connector.MySQLConnection, None, None]:
        """
        Context manager for database connections
        Ensures connections are always properly closed
        
        Args:
            config: Optional custom connection config
            
        Yields:
            MySQL connection object
            
        Raises:
            DatabaseError: If connection fails
        """
        connection = None
        try:
            # Use provided config or default
            connection_config = config or db_config.get_mysql_config()
            
            logger.debug(f"Connecting to database: {connection_config['host']}")
            connection = mysql.connector.connect(**connection_config)
            
            yield connection
            
        except mysql.connector.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {e}")
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
                logger.debug("Database connection closed")
    
    @staticmethod
    @contextmanager
    def get_cursor(connection: mysql.connector.MySQLConnection, 
                   dictionary: bool = True) -> Generator[mysql.connector.cursor.MySQLCursor, None, None]:
        """
        Context manager for database cursors
        
        Args:
            connection: MySQL connection object
            dictionary: Whether to return results as dictionaries
            
        Yields:
            MySQL cursor object
        """
        cursor = None
        try:
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
        finally:
            if cursor:
                cursor.close()
                logger.debug("Database cursor closed")


class QueryExecutor:
    """Safe query executor with proper error handling"""
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, 
                     fetch_one: bool = False, 
                     fetch_all: bool = True,
                     config: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Execute a database query safely with proper connection management
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Whether to fetch only one result
            fetch_all: Whether to fetch all results
            config: Optional connection config
            
        Returns:
            Query results or None
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with ConnectionManager.get_connection(config) as conn:
                with ConnectionManager.get_cursor(conn) as cursor:
                    
                    logger.debug(f"Executing query: {query}")
                    if params:
                        logger.debug(f"Query parameters: {params}")
                        
                    cursor.execute(query, params or ())
                    
                    if fetch_one:
                        result = cursor.fetchone()
                        logger.debug(f"Query returned one result: {bool(result)}")
                        return result
                    elif fetch_all:
                        result = cursor.fetchall()
                        logger.debug(f"Query returned {len(result)} results")
                        return result
                    else:
                        # For INSERT, UPDATE, DELETE operations
                        conn.commit()
                        affected_rows = cursor.rowcount
                        logger.debug(f"Query affected {affected_rows} rows")
                        return affected_rows
                        
        except mysql.connector.Error as e:
            logger.error(f"Query execution error: {e}")
            raise DatabaseError(f"Query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected query error: {e}")
            raise DatabaseError(f"Unexpected query error: {e}")
    
    @staticmethod
    def execute_transaction(queries: List[tuple], 
                           config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute multiple queries in a transaction
        
        Args:
            queries: List of (query, params) tuples
            config: Optional connection config
            
        Returns:
            True if transaction successful, False otherwise
            
        Raises:
            DatabaseError: If transaction fails
        """
        try:
            with ConnectionManager.get_connection(config) as conn:
                with ConnectionManager.get_cursor(conn) as cursor:
                    
                    # Start transaction
                    conn.start_transaction()
                    
                    try:
                        for query, params in queries:
                            logger.debug(f"Executing transaction query: {query}")
                            cursor.execute(query, params or ())
                        
                        # Commit transaction
                        conn.commit()
                        logger.info(f"Transaction completed successfully ({len(queries)} queries)")
                        return True
                        
                    except Exception as e:
                        # Rollback on error
                        conn.rollback()
                        logger.error(f"Transaction rolled back due to error: {e}")
                        raise
                        
        except mysql.connector.Error as e:
            logger.error(f"Transaction error: {e}")
            raise DatabaseError(f"Transaction failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected transaction error: {e}")
            raise DatabaseError(f"Unexpected transaction error: {e}")


class DatabaseHealthChecker:
    """Database health and connectivity checker"""
    
    @staticmethod
    def check_connection(config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if database connection is healthy
        
        Args:
            config: Optional connection config
            
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with ConnectionManager.get_connection(config) as conn:
                with ConnectionManager.get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def check_table_exists(table_name: str, 
                          config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if a specific table exists
        
        Args:
            table_name: Name of the table to check
            config: Optional connection config
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
            """
            
            db_name = (config or db_config.get_mysql_config())['database']
            result = QueryExecutor.execute_query(
                query, (db_name, table_name), fetch_one=True, config=config
            )
            
            return result and result.get('count', 0) > 0
            
        except Exception as e:
            logger.warning(f"Table existence check failed for {table_name}: {e}")
            return False


# Legacy compatibility functions
def obtener_conexion():
    """
    Legacy function for backward compatibility
    Returns a connection that must be manually closed
    """
    try:
        config = db_config.get_mysql_config()
        return mysql.connector.connect(**config)
    except mysql.connector.Error as e:
        raise DatabaseError(f"Failed to get connection: {e}")


# Convenience instances
query_executor = QueryExecutor()
health_checker = DatabaseHealthChecker()
