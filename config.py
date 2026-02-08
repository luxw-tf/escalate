"""
Configuration module for Escalate Telegram Bot
Loads environment variables and validates configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Blockchain Configuration
    MONAD_RPC_URL = os.getenv("MONAD_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
    USDC_ADDRESS = os.getenv("USDC_ADDRESS")
    RESOLVER_ADDRESS = os.getenv("RESOLVER_ADDRESS")
    
    # USDC Configuration
    USDC_DECIMALS = 6  # Standard USDC decimals
    
    # Market Configuration
    MIN_MARKET_DURATION_MINUTES = 5
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "MONAD_RPC_URL",
            "PRIVATE_KEY",
            "CONTRACT_ADDRESS",
            "USDC_ADDRESS",
            "RESOLVER_ADDRESS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file"
            )
        
        # Validate addresses format
        if cls.CONTRACT_ADDRESS and not cls.CONTRACT_ADDRESS.startswith("0x"):
            raise ValueError("CONTRACT_ADDRESS must start with 0x")
        if cls.USDC_ADDRESS and not cls.USDC_ADDRESS.startswith("0x"):
            raise ValueError("USDC_ADDRESS must start with 0x")
        if cls.RESOLVER_ADDRESS and not cls.RESOLVER_ADDRESS.startswith("0x"):
            raise ValueError("RESOLVER_ADDRESS must start with 0x")
        
        return True

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    print("Please create a .env file with all required variables")
