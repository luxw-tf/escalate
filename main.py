"""
Escalate Telegram Bot - Main Entry Point
Production-grade prediction market bot for Monad testnet
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from services.blockchain import BlockchainService
from bot.handlers import start, markets, create, bet, resolve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("✅ Configuration validated")
        
        # Test blockchain connection
        blockchain = BlockchainService()
        is_connected = await blockchain.check_connection()
        
        if not is_connected:
            logger.warning("⚠️  Failed to connect to blockchain - bot will start but blockchain features may not work")
            logger.warning(f"⚠️  RPC URL: {Config.MONAD_RPC_URL}")
        else:
            logger.info(f"✅ Connected to blockchain at {Config.MONAD_RPC_URL}")
            logger.info(f"✅ Wallet address: {blockchain.wallet_address}")
        
        # Initialize bot and dispatcher
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Register routers
        dp.include_router(start.router)
        dp.include_router(markets.router)
        dp.include_router(create.router)
        dp.include_router(bet.router)
        dp.include_router(resolve.router)
        
        logger.info("✅ All handlers registered")
        logger.info("🚀 Starting Escalate bot...")
        
        # Start polling
        await dp.start_polling(bot)
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
