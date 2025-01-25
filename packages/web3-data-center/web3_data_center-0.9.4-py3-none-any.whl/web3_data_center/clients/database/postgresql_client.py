from typing import Dict, Any, List, Union, Optional, cast

import asyncio
import asyncpg
from asyncpg.pool import Pool
from asyncpg.transaction import Transaction
from contextlib import asynccontextmanager
from .base_database_client import BaseDatabaseClient, T
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Manages a database transaction with a connection"""
    
    def __init__(self, connection: asyncpg.Connection, transaction: Transaction):
        self._connection = connection
        self._transaction = transaction
        
    async def execute(self, query: str, *args, timeout: Optional[float] = None) -> str:
        """Execute a query within the transaction
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            Command status string
        """
        return await self._connection.execute(query, *args, timeout=timeout)
        
    async def fetch(self, query: str, *args, timeout: Optional[float] = None) -> List[asyncpg.Record]:
        """Execute a query and return results
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            List of records
        """
        return await self._connection.fetch(query, *args, timeout=timeout)
        
    async def fetchval(self, query: str, *args, timeout: Optional[float] = None) -> Any:
        """Execute a query and return a single value
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            Single value from first row
        """
        return await self._connection.fetchval(query, *args, timeout=timeout)
        
    async def fetchrow(self, query: str, *args, timeout: Optional[float] = None) -> Optional[asyncpg.Record]:
        """Execute a query and return first row
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds
            
        Returns:
            First row or None
        """
        return await self._connection.fetchrow(query, *args, timeout=timeout)

class PostgreSQLClient(BaseDatabaseClient[Dict[str, Any]]):
    """PostgreSQL database client
    
    Features:
    - Connection pooling
    - Transaction management
    - Batch operations
    - Query execution with parameter binding
    - Schema management
    """
    
    def __init__(self,
                 db_name: str = "postgresql",
                 config_path: str = "config.yml",
                 pool_size: int = 5,
                 max_overflow: int = 10):
        """Initialize PostgreSQL client
        
        Args:
            db_name: Database name in config
            config_path: Path to config file
            pool_size: Initial size of the connection pool
            max_overflow: Maximum number of connections that can be created beyond pool_size
        """
        super().__init__(db_name, config_path, pool_size, max_overflow)
        self._pool: Optional[Pool] = None
        self._current_transaction: Optional[tuple] = None
        self._transaction_lock = asyncio.Lock()
        
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string from config
        
        Returns:
            PostgreSQL connection URL
        """
        config = self.db_config
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        database = config.get('database', 'postgres')
        user = config.get('user', 'postgres')
        password = config.get('password', '')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
    async def setup(self) -> None:
        """Set up the PostgreSQL client and establish connection pool"""
        if not self._pool:
            try:
                config = self.db_config
                self._pool = await asyncpg.create_pool(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 5432),
                    user=config.get('user', 'postgres'),
                    password=config.get('password', ''),
                    database=config.get('database', 'postgres'),
                    min_size=self.pool_size,
                    max_size=self.pool_size + self.max_overflow,
                    ssl=config.get('ssl', False),
                    command_timeout=config.get('command_timeout', 60.0)
                )
                logger.info(f"Connected to PostgreSQL database: {config.get('database', 'postgres')}")
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {str(e)}")
                raise
                
    async def close(self) -> None:
        """Close all database connections"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Closed PostgreSQL connection pool")
            
    async def execute(self,
                     query: str,
                     parameters: Optional[Union[List[Any], Dict[str, Any]]] = None,
                     timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        """Execute a PostgreSQL query
        
        Args:
            query: SQL query
            parameters: Query parameters (list for positional, dict for named)
            timeout: Query timeout in seconds
            
        Returns:
            List of query results as dictionaries
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
            
        try:
            if self._current_transaction:
                conn, _ = self._current_transaction
            else:
                async with self._pool.acquire() as conn:
                    if parameters:
                        result = await conn.fetch(query, *parameters if isinstance(parameters, list) else parameters, timeout=timeout)
                    else:
                        result = await conn.fetch(query, timeout=timeout)
                    return [dict(r) for r in result]
                    
            # If in transaction
            if parameters:
                result = await conn.fetch(query, *parameters if isinstance(parameters, list) else parameters, timeout=timeout)
            else:
                result = await conn.fetch(query, timeout=timeout)
            return [dict(r) for r in result]
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
            
    async def execute_many(self,
                         query: str,
                         parameters: List[Union[List[Any], Dict[str, Any]]],
                         timeout: Optional[float] = None) -> None:
        """Execute same query with multiple sets of parameters
        
        Args:
            query: SQL query
            parameters: List of parameter sets
            timeout: Query timeout in seconds
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
            
        try:
            if self._current_transaction:
                conn, _ = self._current_transaction
            else:
                async with self._pool.acquire() as conn:
                    await conn.executemany(query, parameters, timeout=timeout)
                    return
                    
            # If in transaction
            await conn.executemany(query, parameters, timeout=timeout)
            
        except Exception as e:
            logger.error(f"Error executing batch query: {str(e)}")
            raise
            
    async def begin_transaction(self) -> Transaction:
        """Begin a new transaction
        
        Returns:
            Transaction object
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
            
        if self._current_transaction:
            raise RuntimeError("Transaction already in progress")
            
        try:
            conn = await self._pool.acquire()
            transaction = conn.transaction()
            await transaction.start()
            self._current_transaction = (conn, transaction)
            return transaction
        except Exception as e:
            logger.error(f"Error starting transaction: {str(e)}")
            raise
            
    async def commit(self) -> None:
        """Commit the current transaction"""
        if not self._current_transaction:
            raise RuntimeError("No transaction in progress")
            
        try:
            conn, transaction = self._current_transaction
            await transaction.commit()
        finally:
            if self._pool and conn:
                await self._pool.release(conn)
            self._current_transaction = None
            
    async def rollback(self) -> None:
        """Rollback the current transaction"""
        if not self._current_transaction:
            raise RuntimeError("No transaction in progress")
            
        try:
            conn, transaction = self._current_transaction
            await transaction.rollback()
        finally:
            if self._pool and conn:
                await self._pool.release(conn)
            self._current_transaction = None
            
    @asynccontextmanager
    async def transaction(self):
        """Start a new transaction
        
        Returns:
            TransactionManager that wraps the connection and transaction
        """
        async with self._transaction_lock:
            try:
                transaction = await self.begin_transaction()
                conn, tx = self._current_transaction
                yield TransactionManager(conn, tx)
                await self.commit()
            except Exception:
                await self.rollback()
                raise
                
    def _get_insert_query(self) -> str:
        """Get the insert query for batch processing
        
        This should be overridden by specific implementations to provide
        the correct insert query.
        
        Returns:
            Insert query string
        """
        raise NotImplementedError("Insert query not implemented")
        
    def _get_create_table_query(self, table_name: str, schema: Dict[str, Any]) -> str:
        """Get query to create a PostgreSQL table
        
        Args:
            table_name: Name of the table
            schema: Table schema definition with column names and types
            
        Returns:
            CREATE TABLE query
        """
        columns = []
        for column_name, column_def in schema.items():
            if isinstance(column_def, str):
                columns.append(f"{column_name} {column_def}")
            elif isinstance(column_def, dict):
                col_type = column_def.get('type', 'TEXT')
                constraints = column_def.get('constraints', [])
                columns.append(f"{column_name} {col_type} {' '.join(constraints)}")
                
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {','.join(columns)}
            );
        """
        
    async def _create_connection(self) -> None:
        """Create a new database connection"""
        if not self._pool:
            try:
                config = self.db_config
                self._pool = await asyncpg.create_pool(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 5432),
                    user=config.get('user', 'postgres'),
                    password=config.get('password', ''),
                    database=config.get('database', 'postgres'),
                    min_size=self.pool_size,
                    max_size=self.pool_size + self.max_overflow,
                    ssl=config.get('ssl', False),
                    command_timeout=config.get('command_timeout', 60.0)
                )
                logger.info(f"Connected to PostgreSQL database: {config.get('database', 'postgres')}")
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {str(e)}")
                raise

    async def _close_connection(self) -> None:
        """Close the database connection"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Closed PostgreSQL connection pool")

    async def connect(self) -> None:
        """Connect to PostgreSQL database"""
        await self.setup()
        
    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL database"""
        await self.close()
        
    async def execute_query(self, query: str, *args) -> str:
        """Execute a query and return the status
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Query status string
        """
        return await self.execute(query, parameters=list(args))
        
    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a query and return all results
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of records as dictionaries
        """
        return await self.execute(query, parameters=list(args))
        
    async def fetchval(self, query: str, *args) -> Any:
        """Execute a query and return a single value
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value from first row
        """
        result = await self.execute(query, parameters=list(args))
        return result[0][list(result[0].keys())[0]] if result else None
        
    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a query and return first row
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            First row as dictionary or None
        """
        result = await self.execute(query, parameters=list(args))
        return result[0] if result else None
            
    def _get_insert_query(self) -> str:
        """Get the insert query for batch processing
        
        This should be overridden by specific implementations to provide
        the correct insert query.
        
        Returns:
            Insert query string
        """
        raise NotImplementedError("Insert query not implemented")
        
    def _get_create_table_query(self, table_name: str, schema: Dict[str, Any]) -> str:
        """Get query to create a PostgreSQL table
        
        Args:
            table_name: Name of the table
            schema: Table schema definition with column names and types
            
        Returns:
            CREATE TABLE query
        """
        columns = []
        for column_name, column_def in schema.items():
            if isinstance(column_def, str):
                columns.append(f"{column_name} {column_def}")
            elif isinstance(column_def, dict):
                col_type = column_def.get('type', 'TEXT')
                constraints = column_def.get('constraints', [])
                columns.append(f"{column_name} {col_type} {' '.join(constraints)}")
                
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {','.join(columns)}
            );
        """
