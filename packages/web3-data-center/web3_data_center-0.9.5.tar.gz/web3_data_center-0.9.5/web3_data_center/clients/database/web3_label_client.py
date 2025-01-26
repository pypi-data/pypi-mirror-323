from typing import Dict, Any, List, Optional, Union
import logging
import re
from datetime import datetime
import asyncpg
from .postgresql_client import PostgreSQLClient

logger = logging.getLogger(__name__)

class Web3LabelClient(PostgreSQLClient):
    """Client for managing web3 address labels in the database
    
    Provides functionality for:
    - Adding/updating address labels
    - Querying labels by address
    - Managing label categories and types
    - Batch label operations
    """
    
    def __init__(self,
                 config_path: str = "config.yml",
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 db_name: str = "labels"):
        """Initialize Web3LabelClient
        
        Args:
            config_path: Path to config file
            pool_size: Initial size of the connection pool
            max_overflow: Maximum number of connections beyond pool_size
            db_name: Database name in config
        """
        self.db_name = db_name  # Set db_name before parent initialization
        super().__init__(
            db_name=db_name,
            config_path=config_path,
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        self._address_pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')

    async def _create_connection(self) -> asyncpg.Pool:
        """Create PostgreSQL connection pool
        
        Returns:
            asyncpg.Pool: Connection pool
        """
        config = self.db_config
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        database = config.get('database', 'postgres')
        user = config.get('user', 'postgres')
        password = config.get('password', '')
        
        try:
            pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=self.pool_size,
                max_size=self.pool_size + self.max_overflow
            )
            return pool
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {str(e)}")
            raise

    async def _close_connection(self, pool: asyncpg.Pool) -> None:
        """Close PostgreSQL connection pool
        
        Args:
            pool: Connection pool to close
        """
        await pool.close()

    def _validate_address(self, address: str) -> bool:
        """Validate ethereum address format
        
        Args:
            address: Ethereum address to validate
            
        Returns:
            bool: True if valid address format
        """
        return bool(self._address_pattern.match(address))

    async def setup(self) -> None:
        """Set up database connection pool"""
        if not self._pool:
            self._pool = await self._create_connection()

    async def add_label(self,
                       address: str,
                       label: str,
                       category: str,
                       source: str,
                       confidence: float = 1.0,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add or update a label for an address
        
        Args:
            address: Ethereum address
            label: Label text
            category: Label category (e.g. 'exchange', 'contract', etc)
            source: Source of the label
            confidence: Confidence score between 0-1
            metadata: Optional additional metadata
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If address format is invalid
        """
        if not self._validate_address(address):
            raise ValueError(f"Invalid ethereum address format: {address}")
            
        query = """
        INSERT INTO address_labels 
            (address, label, category, source, confidence, metadata, created_at, updated_at)
        VALUES 
            ($1, $2, $3, $4, $5, $6, $7, $7)
        ON CONFLICT (address, label, category) 
        DO UPDATE SET
            confidence = EXCLUDED.confidence,
            metadata = COALESCE(address_labels.metadata::jsonb || EXCLUDED.metadata::jsonb, EXCLUDED.metadata::jsonb),
            updated_at = EXCLUDED.updated_at
        """
        
        now = datetime.utcnow()
        try:
            await self.execute(
                query,
                address.lower(),
                label,
                category,
                source,
                confidence,
                metadata or {},
                now
            )
            return True
        except Exception as e:
            logger.error(f"Error adding label for {address}: {str(e)}")
            return False

    async def get_labels(self,
                        address: str,
                        category: Optional[str] = None,
                        min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get all labels for an address
        
        Args:
            address: Ethereum address
            category: Optional category filter
            min_confidence: Minimum confidence threshold
            
        Returns:
            List[Dict]: List of label records
        """
        if not self._validate_address(address):
            raise ValueError(f"Invalid ethereum address format: {address}")
            
        query = """
        SELECT address, label, category, source, confidence, metadata, created_at, updated_at
        FROM address_labels
        WHERE address = $1
        AND confidence >= $2
        """
        params = [address.lower(), min_confidence]
        
        if category:
            query += " AND category = $3"
            params.append(category)
            
        query += " ORDER BY confidence DESC, updated_at DESC"
        
        try:
            return await self.fetch_all(query, *params)
        except Exception as e:
            logger.error(f"Error fetching labels for {address}: {str(e)}")
            return []

    async def get_addresses_by_label(self,
                                   label: str,
                                   category: Optional[str] = None,
                                   min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get all addresses with a specific label
        
        Args:
            label: Label text to search for
            category: Optional category filter
            min_confidence: Minimum confidence threshold
            
        Returns:
            List[Dict]: List of address records with matching label
        """
        query = """
        SELECT address, label, category, source, confidence, metadata, created_at, updated_at
        FROM address_labels
        WHERE label ILIKE $1
        AND confidence >= $2
        """
        params = [f"%{label}%", min_confidence]
        
        if category:
            query += " AND category = $3"
            params.append(category)
            
        query += " ORDER BY confidence DESC, updated_at DESC"
        
        try:
            return await self.fetch_all(query, *params)
        except Exception as e:
            logger.error(f"Error fetching addresses for label {label}: {str(e)}")
            return []

    async def delete_label(self,
                          address: str,
                          label: Optional[str] = None,
                          category: Optional[str] = None) -> bool:
        """Delete labels for an address
        
        Args:
            address: Ethereum address
            label: Optional specific label to delete
            category: Optional category filter
            
        Returns:
            bool: True if successful
        """
        if not self._validate_address(address):
            raise ValueError(f"Invalid ethereum address format: {address}")
            
        query = "DELETE FROM address_labels WHERE address = $1"
        params = [address.lower()]
        
        if label:
            query += " AND label = $2"
            params.append(label)
            
        if category:
            query += f" AND category = ${len(params) + 1}"
            params.append(category)
            
        try:
            await self.execute(query, *params)
            return True
        except Exception as e:
            logger.error(f"Error deleting labels for {address}: {str(e)}")
            return False

    async def get_categories(self) -> List[str]:
        """Get all unique label categories
        
        Returns:
            List[str]: List of category names
        """
        query = "SELECT DISTINCT category FROM address_labels ORDER BY category"
        try:
            results = await self.fetch_all(query)
            return [r['category'] for r in results]
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return []

    async def get_addresses_labels(self, addresses: List[str]) -> List[Dict[str, Any]]:
        """Get labels for multiple addresses
        
        Args:
            addresses: List of addresses to get labels for
            
        Returns:
            List of label info dicts for each address
        """
        if not addresses:
            return []
            
        # Normalize addresses
        addresses = [addr.lower() for addr in addresses if self._address_pattern.match(addr)]
        if not addresses:
            return []
            
        # Query labels
        query = """
            SELECT 
                mca.address,
                me.entity,
                me.category AS type,
                mca.name_tag,
                mca.entity,
                mca.labels,
                mca.is_ca,
                mca.is_seed
            FROM multi_chain_addresses mca
            LEFT JOIN multi_entity me ON mca.entity = me.entity
            WHERE mca.chain_id = 0 AND mca.address = ANY($1::text[])
        """
        
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, addresses)
                
            # Process results
            results = []
            seen_addresses = set()
            for row in rows:
                type_str = row['type'] if row['type'] is not None else ''
                addr = row['address']
                seen_addresses.add(addr)
                results.append({
                    'address': addr,
                    'label': row['labels'].split(',')[0] if row['labels'] else None,  # Use first label as primary
                    'name_tag': row['name_tag'],
                    'type': type_str,
                    'entity': row['entity'],
                    'is_cex': 'CEX' in type_str.upper() or 'EXCHANGE' in type_str.upper()
                })
                
            # Add empty results for addresses without labels
            for addr in addresses:
                if addr not in seen_addresses:
                    results.append({
                        'address': addr,
                        'label': None,
                        'name_tag': None,
                        'type': None,
                        'entity': None,
                        'is_cex': False
                    })
                    
            return results
            
        except Exception as e:
            logger.error(f"Error getting labels for addresses: {str(e)}")
            return [{
                'address': addr,
                'label': None,
                'name_tag': None,
                'type': None,
                'entity': None,
                'is_cex': False
            } for addr in addresses]
