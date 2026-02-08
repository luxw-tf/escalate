"""
Market viewing handlers
Displays markets in Polymarket style with pools and liquidity
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from services.blockchain import BlockchainService
from bot.keyboards import get_market_list_keyboard, get_market_detail_keyboard

router = Router()


def format_time_remaining(expiry: int) -> str:
    """Format time remaining until expiry"""
    now = int(datetime.utcnow().timestamp())
    remaining = expiry - now
    
    if remaining <= 0:
        return "Expired"
    
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    
    if hours > 24:
        days = hours // 24
        return f"{days}d {hours % 24}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def format_market_summary(market: dict, blockchain: BlockchainService) -> str:
    """Format market summary in Polymarket style"""
    total_yes = blockchain.parse_mon_amount(market['total_yes'])
    total_no = blockchain.parse_mon_amount(market['total_no'])
    total_liquidity = total_yes + total_no
    
    time_remaining = format_time_remaining(market['expiry'])
    
    # Calculate implied probability
    if total_liquidity > 0:
        yes_prob = (total_yes / total_liquidity) * 100
    else:
        yes_prob = 50.0
    
    text = (
        f"*Market #{market['id']}*\n"
        f"❓ {market['question']}\n\n"
        f"📊 *Pools:*\n"
        f"  ✅ YES: {total_yes:.2f} MON ({yes_prob:.1f}%)\n"
        f"  ❌ NO: {total_no:.2f} MON ({100-yes_prob:.1f}%)\n\n"
        f"💰 *Total Liquidity:* {total_liquidity:.2f} MON\n"
        f"⏰ *Expires in:* {time_remaining}\n"
    )
    
    if market['resolved']:
        outcome_text = "YES ✅" if market['outcome'] else "NO ❌"
        text += f"\n🏁 *Resolved:* {outcome_text}"
    
    return text


@router.callback_query(F.data == "view_markets")
async def view_markets(callback: CallbackQuery, state: FSMContext):
    """Display all active markets"""
    await callback.answer("Loading markets...")
    
    try:
        blockchain = BlockchainService()
        
        # Get market count
        market_count = await blockchain.get_market_count()
        
        if market_count == 0:
            await callback.message.edit_text(
                "📊 *No markets available*\n\n"
                "Be the first to create a market!",
                parse_mode="Markdown"
            )
            return
        
        # Fetch all markets
        active_markets = []
        now = int(datetime.utcnow().timestamp())
        
        for market_id in range(1, market_count + 1):
            market = await blockchain.get_market(market_id)
            
            if market and not market['resolved'] and market['expiry'] > now:
                active_markets.append(market)
        
        if not active_markets:
            await callback.message.edit_text(
                "📊 *No active markets*\n\n"
                "All markets have expired or been resolved.",
                parse_mode="Markdown"
            )
            return
        
        # Format market list
        header = (
            "📊 *Active Prediction Markets*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        markets_text = ""
        for market in active_markets[:5]:  # Show first 5 markets
            markets_text += format_market_summary(market, blockchain) + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        
        full_text = header + markets_text
        
        await callback.message.edit_text(
            full_text,
            reply_markup=get_market_list_keyboard(active_markets[:5]),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Error loading markets*\n\n"
            f"Failed to fetch markets from blockchain.\n"
            f"Error: {str(e)}",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("view_market_"))
async def view_market_detail(callback: CallbackQuery, state: FSMContext):
    """Display detailed view of a specific market"""
    market_id = int(callback.data.split("_")[2])
    
    try:
        blockchain = BlockchainService()
        market = await blockchain.get_market(market_id)
        
        if not market:
            await callback.answer("Market not found", show_alert=True)
            return
        
        market_text = format_market_summary(market, blockchain)
        
        await callback.message.edit_text(
            market_text,
            reply_markup=get_market_detail_keyboard(market_id),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Error: {str(e)}", show_alert=True)
