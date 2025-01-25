# web3_data_center/web3_data_center/clients/api/etherscan_client.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from ..mixins import AuthMixin, RateLimitMixin
from ..mixins.auth import AuthType

@dataclass
class EndpointConfig:
    """Configuration for API endpoints"""
    path: str
    method: str = "GET"
    batch_size: Optional[int] = None
    rate_limit: Optional[float] = None
    cost_weight: float = 1.0

class EtherscanClient(BaseAPIClient, AuthMixin, RateLimitMixin):
    """Etherscan API client"""
    
    # API endpoint configurations
    ENDPOINTS = {
        'contract_creation': EndpointConfig(
            path="/api",
            batch_size=50,
            rate_limit=3.0,
            cost_weight=2.0
        ),
        'account_balance': EndpointConfig(
            path="/api",
            batch_size=20,
            rate_limit=5.0
        ),
        'account_txlist': EndpointConfig(
            path="/api",
            batch_size=100,
            rate_limit=5.0
        ),
        'account_tokentx': EndpointConfig(
            path="/api",
            batch_size=100,
            rate_limit=5.0
        ),
        'account_nfttx': EndpointConfig(
            path="/api",
            batch_size=100,
            rate_limit=5.0
        ),
        'account_internal_txs': EndpointConfig(
            path="/api",
            batch_size=100,
            rate_limit=5.0
        )
    }
    
    def __init__(self, config_path: str = "config.yml", use_proxy: bool = True):
        """Initialize Etherscan client"""
        super().__init__("etherscan", config_path, use_proxy)
        
        # Setup authentication and rate limits
        self.setup_auth(AuthType.API_KEY)
        self.setup_rate_limits(self.ENDPOINTS)
        
    @RateLimitMixin.rate_limited('contract_creation')
    async def get_deployment(self, address: str) -> Optional[Dict[str, Any]]:
        """Get contract deployment information"""
        params = {
            "module": "contract",
            "action": "getcontractcreation",
            "contractaddresses": address
        }
        
        params, headers = await self.authenticate_request(
            "GET", "/api", params, {}
        )
        
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result', [{}])[0] if result else None
        
    async def get_deployments(self, addresses: List[str]) -> List[Dict[str, Any]]:
        """Get contract deployments in batches"""
        config = self.ENDPOINTS['contract_creation']
        results = []
        
        for i in range(0, len(addresses), config.batch_size):
            batch = addresses[i:i + config.batch_size]
            params = {
                "module": "contract",
                "action": "getcontractcreation",
                "contractaddresses": ','.join(batch)
            }
            
            params, headers = await self.authenticate_request(
                "GET", "/api", params, {}
            )
            
            result = await self._make_request("/api", params=params, headers=headers)
            if result and 'result' in result:
                results.extend(result['result'])
                
        return results
        
    @RateLimitMixin.rate_limited('account_balance')
    async def get_eth_balance(self, address: str) -> Optional[str]:
        """Get ETH balance for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            Balance in wei as string, or None if error
        """
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest"
        }
        
        params, headers = await self.authenticate_request("GET", "/api", params, {})
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result') if result else None
        
    async def get_eth_balances(self, addresses: List[str]) -> Dict[str, Optional[str]]:
        """Get ETH balances for multiple addresses
        
        Args:
            addresses: List of Ethereum addresses
            
        Returns:
            Dict mapping addresses to balances in wei
        """
        config = self.ENDPOINTS['account_balance']
        results = {}
        
        for i in range(0, len(addresses), config.batch_size):
            batch = addresses[i:i + config.batch_size]
            params = {
                "module": "account",
                "action": "balancemulti",
                "address": ','.join(batch),
                "tag": "latest"
            }
            
            params, headers = await self.authenticate_request("GET", "/api", params, {})
            result = await self._make_request("/api", params=params, headers=headers)
            
            if result and 'result' in result:
                for item in result['result']:
                    results[item['account']] = item['balance']
                    
        return results
        
    @RateLimitMixin.rate_limited('account_txlist')
    async def get_normal_txs(self, address: str, startblock: int = 0, endblock: int = 99999999, 
                           page: int = 1, offset: int = 100, sort: str = "asc") -> List[Dict[str, Any]]:
        """Get list of normal transactions for an address
        
        Args:
            address: Ethereum address
            startblock: Start block number
            endblock: End block number
            page: Page number
            offset: Max records to return
            sort: Sort order (asc/desc)
            
        Returns:
            List of transaction objects
        """
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": str(startblock),
            "endblock": str(endblock),
            "page": str(page),
            "offset": str(offset),
            "sort": sort
        }
        
        params, headers = await self.authenticate_request("GET", "/api", params, {})
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result', []) if result else []
        
    @RateLimitMixin.rate_limited('account_internal_txs')
    async def get_internal_txs(self, address: str, startblock: int = 0, endblock: int = 99999999,
                             page: int = 1, offset: int = 100, sort: str = "asc") -> List[Dict[str, Any]]:
        """Get list of internal transactions for an address
        
        Args:
            address: Ethereum address
            startblock: Start block number
            endblock: End block number
            page: Page number
            offset: Max records to return
            sort: Sort order (asc/desc)
            
        Returns:
            List of transaction objects
        """
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": str(startblock),
            "endblock": str(endblock),
            "page": str(page),
            "offset": str(offset),
            "sort": sort
        }
        
        params, headers = await self.authenticate_request("GET", "/api", params, {})
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result', []) if result else []
        
    @RateLimitMixin.rate_limited('account_tokentx')
    async def get_token_transfers(self, address: str, contractaddress: Optional[str] = None,
                                startblock: int = 0, endblock: int = 99999999,
                                page: int = 1, offset: int = 100, sort: str = "asc") -> List[Dict[str, Any]]:
        """Get list of ERC20 token transfers for an address
        
        Args:
            address: Ethereum address
            contractaddress: Token contract address (optional)
            startblock: Start block number
            endblock: End block number
            page: Page number
            offset: Max records to return
            sort: Sort order (asc/desc)
            
        Returns:
            List of token transfer objects
        """
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": str(startblock),
            "endblock": str(endblock),
            "page": str(page),
            "offset": str(offset),
            "sort": sort
        }
        
        if contractaddress:
            params["contractaddress"] = contractaddress
            
        params, headers = await self.authenticate_request("GET", "/api", params, {})
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result', []) if result else []
        
    @RateLimitMixin.rate_limited('account_nfttx')
    async def get_nft_transfers(self, address: str, contractaddress: Optional[str] = None,
                              startblock: int = 0, endblock: int = 99999999,
                              page: int = 1, offset: int = 100, sort: str = "asc") -> List[Dict[str, Any]]:
        """Get list of ERC721/ERC1155 NFT transfers for an address
        
        Args:
            address: Ethereum address
            contractaddress: NFT contract address (optional)
            startblock: Start block number
            endblock: End block number
            page: Page number
            offset: Max records to return
            sort: Sort order (asc/desc)
            
        Returns:
            List of NFT transfer objects
        """
        params = {
            "module": "account",
            "action": "tokennfttx",
            "address": address,
            "startblock": str(startblock),
            "endblock": str(endblock),
            "page": str(page),
            "offset": str(offset),
            "sort": sort
        }
        
        if contractaddress:
            params["contractaddress"] = contractaddress
            
        params, headers = await self.authenticate_request("GET", "/api", params, {})
        result = await self._make_request("/api", params=params, headers=headers)
        return result.get('result', []) if result else []