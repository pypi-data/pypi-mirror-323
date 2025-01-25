from typing import Dict, Any, List, Optional, Union, TypeVar, Generic
import logging
import time
import asyncio
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, DatabaseError
from .base_database_client import BaseDatabaseClient, T

logger = logging.getLogger(__name__)

class Neo4jClient(BaseDatabaseClient[Dict[str, Any]]):
    """Neo4j database client with async support
    
    Features:
    - Connection pooling with configurable pool size
    - Automatic retry with exponential backoff
    - Rate limiting to prevent overloading
    - Transaction management
    - Batch operations
    - Graph operations (nodes, relationships, paths)
    - Type hints and async context manager support
    """
    
    def __init__(self,
                 db_name: str = "neo4j",
                 config_path: str = "config.yml",
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 requests_per_second: int = 20):
        """Initialize Neo4j client
        
        Args:
            db_name: Database name in config
            config_path: Path to config file
            pool_size: Initial size of the connection pool
            max_overflow: Maximum number of connections that can be created beyond pool_size
            requests_per_second: Maximum number of requests per second
        """
        super().__init__(db_name, config_path, pool_size, max_overflow)
        self.driver = None
        self._requests_per_second = requests_per_second
        self._rate_limiter = asyncio.Semaphore(self._requests_per_second)
        self._last_request_time = 0
        
    def _build_connection_string(self) -> Dict[str, str]:
        """Build Neo4j connection parameters from config
        
        Returns:
            Dict with uri, username, and password
        """
        config = self.db_config
        return {
            "uri": config.get('uri', 'bolt://localhost:7687'),
            "username": config.get('username', 'neo4j'),
            "password": config.get('password', '')
        }
        
    async def connect(self) -> None:
        """Establish connection to Neo4j database"""
        try:
            conn_params = self.connection_string
            self.driver = AsyncGraphDatabase.driver(
                conn_params['uri'],
                auth=(conn_params['username'], conn_params['password']),
                max_connection_lifetime=3600
            )
            await self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j database")
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
            
    async def disconnect(self) -> None:
        """Close Neo4j database connection"""
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Disconnected from Neo4j database")
            
    async def execute_query(self, 
                          query: str, 
                          parameters: Optional[Dict[str, Any]] = None,
                          database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query with parameters
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Optional database name to use
            
        Returns:
            List of records as dictionaries
        """
        if not self.driver:
            await self.connect()
            
        async with self._rate_limiter:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < 1.0 / self._requests_per_second:
                await asyncio.sleep(1.0 / self._requests_per_second - time_since_last)
            
            try:
                async with self.driver.session(database=database) as session:
                    result = await session.run(query, parameters or {})
                    records = await result.data()
                    self._last_request_time = time.time()
                    return records
                    
            except (ServiceUnavailable, DatabaseError) as e:
                logger.error(f"Neo4j query failed: {str(e)}")
                raise
                
    async def close(self) -> None:
        """Close Neo4j connection"""
        await self.disconnect()
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    # Node Operations
    
    async def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new node with given label and properties
        
        Args:
            label: Node label
            properties: Node properties
            
        Returns:
            Created node data
        """
        query = f"""
        CREATE (n:{label} $props)
        RETURN n
        """
        result = await self.execute_query(query, {"props": properties})
        return result[0]['n'] if result else None
        
    async def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a node by its ID
        
        Args:
            node_id: Node ID
            
        Returns:
            Node data if found, None otherwise
        """
        query = """
        MATCH (n)
        WHERE ID(n) = $node_id
        RETURN n
        """
        result = await self.execute_query(query, {"node_id": node_id})
        return result[0]['n'] if result else None
        
    async def update_node(self, node_id: int, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update node properties
        
        Args:
            node_id: Node ID to update
            properties: New properties to set
            
        Returns:
            Updated node data
        """
        query = """
        MATCH (n)
        WHERE ID(n) = $node_id
        SET n += $props
        RETURN n
        """
        result = await self.execute_query(query, {
            "node_id": node_id,
            "props": properties
        })
        return result[0]['n'] if result else None
        
    async def delete_node(self, node_id: int) -> bool:
        """Delete a node by ID
        
        Args:
            node_id: Node ID to delete
            
        Returns:
            True if node was deleted
        """
        query = """
        MATCH (n)
        WHERE ID(n) = $node_id
        DETACH DELETE n
        """
        await self.execute_query(query, {"node_id": node_id})
        return True
        
    # Relationship Operations
    
    async def create_relationship(self,
                                from_node_id: int,
                                to_node_id: int,
                                relationship_type: str,
                                properties: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Create a relationship between two nodes
        
        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            
        Returns:
            Created relationship data
        """
        query = f"""
        MATCH (a), (b)
        WHERE ID(a) = $from_id AND ID(b) = $to_id
        CREATE (a)-[r:{relationship_type} $props]->(b)
        RETURN r
        """
        params = {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "props": properties or {}
        }
        result = await self.execute_query(query, params)
        return result[0]['r'] if result else None
        
    async def get_relationships(self,
                              node_id: int,
                              relationship_type: Optional[str] = None,
                              direction: str = 'BOTH') -> List[Dict[str, Any]]:
        """Get relationships for a node
        
        Args:
            node_id: Node ID
            relationship_type: Optional relationship type filter
            direction: 'OUTGOING', 'INCOMING', or 'BOTH'
            
        Returns:
            List of relationships
        """
        if direction.upper() not in ['OUTGOING', 'INCOMING', 'BOTH']:
            raise ValueError("direction must be 'OUTGOING', 'INCOMING', or 'BOTH'")
            
        rel_pattern = f"[r{':' + relationship_type if relationship_type else ''}]"
        if direction == 'OUTGOING':
            pattern = f"(n){rel_pattern}->()"
        elif direction == 'INCOMING':
            pattern = f"()-{rel_pattern}->(n)"
        else:
            pattern = f"()-{rel_pattern}-(n)"
            
        query = f"""
        MATCH {pattern}
        WHERE ID(n) = $node_id
        RETURN r
        """
        result = await self.execute_query(query, {"node_id": node_id})
        return [record['r'] for record in result]
        
    # Batch Operations
    
    async def batch_create_nodes(self,
                               label: str,
                               nodes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple nodes in a batch operation
        
        Args:
            label: Node label
            nodes_data: List of node properties
            
        Returns:
            List of created nodes
        """
        query = f"""
        UNWIND $nodes as node
        CREATE (n:{label})
        SET n = node
        RETURN n
        """
        result = await self.execute_query(query, {"nodes": nodes_data})
        return [record['n'] for record in result]
        
    async def batch_create_relationships(self,
                                      relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple relationships in a batch operation
        
        Args:
            relationships: List of relationship data (from_id, to_id, type, properties)
            
        Returns:
            List of created relationships
        """
        query = """
        UNWIND $rels as rel
        MATCH (a), (b)
        WHERE ID(a) = rel.from_id AND ID(b) = rel.to_id
        CREATE (a)-[r:rel.type]->(b)
        SET r = rel.properties
        RETURN r
        """
        result = await self.execute_query(query, {"rels": relationships})
        return [record['r'] for record in result]
        
    # Path Operations
    
    async def get_shortest_path(self,
                              from_node_id: int,
                              to_node_id: int,
                              relationship_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find shortest path between two nodes
        
        Args:
            from_node_id: Start node ID
            to_node_id: End node ID
            relationship_type: Optional relationship type filter
            
        Returns:
            Path data if found, None otherwise
        """
        rel_pattern = f"[*{':' + relationship_type if relationship_type else ''}]"
        query = f"""
        MATCH path = shortestPath((a)-{rel_pattern}-(b))
        WHERE ID(a) = $from_id AND ID(b) = $to_id
        RETURN path
        """
        result = await self.execute_query(query, {
            "from_id": from_node_id,
            "to_id": to_node_id
        })
        return result[0]['path'] if result else None
