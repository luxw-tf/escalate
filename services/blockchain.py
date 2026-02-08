"""
Blockchain service for interacting with Escalate smart contract
Handles all Web3 interactions asynchronously
"""
import json
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from eth_account import Account
from config import Config


class BlockchainService:
    """Service for blockchain interactions"""
    
    def __init__(self):
        """Initialize Web3 connection and contracts"""
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(Config.MONAD_RPC_URL))
        
        # Load account from private key
        self.account = Account.from_key(Config.PRIVATE_KEY)
        self.wallet_address = self.account.address
        
        # Load ABIs
        contracts_dir = Path(__file__).parent.parent / "contracts"
        
        with open(contracts_dir / "escalate_abi.json", "r") as f:
            escalate_abi = json.load(f)
        
        with open(contracts_dir / "erc20_abi.json", "r") as f:
            erc20_abi = json.load(f)
        
        # Initialize contract instances
        self.escalate_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(Config.CONTRACT_ADDRESS),
            abi=escalate_abi
        )
        
        self.usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(Config.USDC_ADDRESS),
            abi=erc20_abi
        )
    
    async def _send_transaction(self, transaction) -> Tuple[str, bool]:
        """
        Send a transaction and wait for receipt
        
        Returns:
            Tuple of (transaction_hash, success)
        """
        try:
            # Get nonce
            nonce = await asyncio.to_thread(
                self.w3.eth.get_transaction_count,
                self.wallet_address
            )
            
            # Build transaction
            transaction.update({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': 500000,  # Conservative gas limit
                'gasPrice': await asyncio.to_thread(self.w3.eth.gas_price.__get__, self.w3.eth)
            })
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = await asyncio.to_thread(
                self.w3.eth.send_raw_transaction,
                signed_txn.rawTransaction
            )
            
            # Wait for receipt
            receipt = await asyncio.to_thread(
                self.w3.eth.wait_for_transaction_receipt,
                tx_hash,
                timeout=120
            )
            
            success = receipt['status'] == 1
            return tx_hash.hex(), success
            
        except Exception as e:
            raise Exception(f"Transaction failed: {str(e)}")
    
    async def create_market(self, question: str, expiry: int) -> Tuple[str, int]:
        """
        Create a new prediction market
        
        Args:
            question: Market question
            expiry: Unix timestamp for market expiry
            
        Returns:
            Tuple of (transaction_hash, market_id)
        """
        try:
            # Build transaction
            transaction = self.escalate_contract.functions.createMarket(
                question,
                expiry
            ).build_transaction({})
            
            # Send transaction
            tx_hash, success = await self._send_transaction(transaction)
            
            if not success:
                raise Exception("Market creation transaction failed")
            
            # Get market ID from transaction receipt
            receipt = await asyncio.to_thread(
                self.w3.eth.get_transaction_receipt,
                tx_hash
            )
            
            # Get market count to determine the new market ID
            market_count = await self.get_market_count()
            
            return tx_hash, market_count
            
        except ContractLogicError as e:
            raise Exception(f"Contract error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create market: {str(e)}")
    
    async def get_market_count(self) -> int:
        """Get total number of markets"""
        try:
            count = await asyncio.to_thread(
                self.escalate_contract.functions.marketCount().call
            )
            return count
        except Exception as e:
            raise Exception(f"Failed to get market count: {str(e)}")
    
    async def get_market(self, market_id: int) -> Optional[Dict]:
        """
        Get market details
        
        Args:
            market_id: Market ID
            
        Returns:
            Dictionary with market details or None if not found
        """
        try:
            market_data = await asyncio.to_thread(
                self.escalate_contract.functions.markets(market_id).call
            )
            
            # Parse market data
            market = {
                'id': market_id,
                'question': market_data[0],
                'expiry': market_data[1],
                'total_yes': market_data[2],
                'total_no': market_data[3],
                'resolved': market_data[4],
                'outcome': market_data[5]
            }
            
            return market
            
        except Exception as e:
            return None
    
    async def place_bet(self, market_id: int, side: bool, amount: int) -> str:
        """
        Place a bet on a market
        
        Args:
            market_id: Market ID
            side: True for YES, False for NO
            amount: Amount in USDC (with decimals)
            
        Returns:
            Transaction hash
        """
        try:
            # Build transaction
            transaction = self.escalate_contract.functions.placeBet(
                market_id,
                side,
                amount
            ).build_transaction({})
            
            # Send transaction
            tx_hash, success = await self._send_transaction(transaction)
            
            if not success:
                raise Exception("Bet placement transaction failed")
            
            return tx_hash
            
        except ContractLogicError as e:
            raise Exception(f"Contract error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to place bet: {str(e)}")
    
    async def approve_mon(self, amount: int) -> str:
        """
        Approve MON spending
        
        Args:
            amount: Amount to approve (with decimals)
            
        Returns:
            Transaction hash
        """
        try:
            # Build transaction
            transaction = self.usdc_contract.functions.approve(
                Web3.to_checksum_address(Config.CONTRACT_ADDRESS),
                amount
            ).build_transaction({})
            
            # Send transaction
            tx_hash, success = await self._send_transaction(transaction)
            
            if not success:
                raise Exception("MON approval transaction failed")
            
            return tx_hash
            
        except Exception as e:
            raise Exception(f"Failed to approve MON: {str(e)}")
    
    async def resolve_market(self, market_id: int, outcome: bool) -> str:
        """
        Resolve a market (resolver only)
        
        Args:
            market_id: Market ID
            outcome: True for YES, False for NO
            
        Returns:
            Transaction hash
        """
        try:
            # Check if caller is resolver
            if self.wallet_address.lower() != Config.RESOLVER_ADDRESS.lower():
                raise Exception("Only the resolver can resolve markets")
            
            # Build transaction
            transaction = self.escalate_contract.functions.resolveMarket(
                market_id,
                outcome
            ).build_transaction({})
            
            # Send transaction
            tx_hash, success = await self._send_transaction(transaction)
            
            if not success:
                raise Exception("Market resolution transaction failed")
            
            return tx_hash
            
        except ContractLogicError as e:
            raise Exception(f"Contract error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to resolve market: {str(e)}")
    
    async def check_connection(self) -> bool:
        """Check if Web3 connection is working"""
        try:
            await asyncio.to_thread(lambda: self.w3.eth.block_number)
            return True
        except Exception:
            return False
    
    def format_mon_amount(self, amount: float) -> int:
        """Convert MON amount to token units with decimals"""
        return int(amount * (10 ** Config.USDC_DECIMALS))
    
    def parse_mon_amount(self, amount: int) -> float:
        """Convert token units to MON amount"""
        return amount / (10 ** Config.USDC_DECIMALS)
