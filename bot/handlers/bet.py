"""
Betting handlers
Implements FSM flow for placing bets on markets
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from bot.states import PlaceBetStates
from bot.keyboards import (
    get_confirmation_keyboard,
    get_cancel_keyboard,
    get_main_menu_keyboard,
    get_market_list_keyboard
)
from services.blockchain import BlockchainService

router = Router()


@router.callback_query(F.data == "place_bet")
async def start_place_bet(callback: CallbackQuery, state: FSMContext):
    """Start bet placement flow by showing markets"""
    await callback.answer("Loading markets...")
    
    try:
        blockchain = BlockchainService()
        
        # Get active markets
        market_count = await blockchain.get_market_count()
        
        if market_count == 0:
            await callback.message.edit_text(
                "📊 *No markets available*\n\n"
                "Create a market first!",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # Fetch active markets
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
                reply_markup=get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # Build message with market details
        message_text = "💰 *Select a market to bet on:*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for market in active_markets[:5]:
            total_yes = blockchain.parse_mon_amount(market['total_yes'])
            total_no = blockchain.parse_mon_amount(market['total_no'])
            total_pool = total_yes + total_no
            
            # Calculate expiry time
            expiry_dt = datetime.fromtimestamp(market['expiry'])
            time_left = expiry_dt - datetime.utcnow()
            
            if time_left.days > 0:
                time_str = f"{time_left.days}d {time_left.seconds // 3600}h"
            elif time_left.seconds >= 3600:
                time_str = f"{time_left.seconds // 3600}h {(time_left.seconds % 3600) // 60}m"
            else:
                time_str = f"{time_left.seconds // 60}m"
            
            message_text += (
                f"📈 *Market #{market['id']}*\n"
                f"❓ {market['question']}\n\n"
                f"💰 *Pool:* {total_pool:.2f} MON\n"
                f"  ✅ YES: {total_yes:.2f} MON\n"
                f"  ❌ NO: {total_no:.2f} MON\n"
                f"⏰ *Expires in:* {time_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
        
        await callback.message.edit_text(
            message_text,
            reply_markup=get_market_list_keyboard(active_markets[:5]),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Error loading markets*\n\n{str(e)}",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("bet_yes_") | F.data.startswith("bet_no_"))
async def select_bet_side(callback: CallbackQuery, state: FSMContext):
    """Handle bet side selection"""
    parts = callback.data.split("_")
    side = parts[1]  # "yes" or "no"
    market_id = int(parts[2])
    
    try:
        blockchain = BlockchainService()
        market = await blockchain.get_market(market_id)
        
        if not market:
            await callback.answer("Market not found", show_alert=True)
            return
        
        # Check if market is still active
        now = int(datetime.utcnow().timestamp())
        if market['resolved']:
            await callback.answer("This market has been resolved", show_alert=True)
            return
        
        if market['expiry'] <= now:
            await callback.answer("This market has expired", show_alert=True)
            return
        
        # Save bet details
        await state.update_data(
            market_id=market_id,
            side=side,
            side_bool=(side == "yes"),
            question=market['question']
        )
        await state.set_state(PlaceBetStates.entering_amount)
        
        side_emoji = "✅ YES" if side == "yes" else "❌ NO"
        
        await callback.message.edit_text(
            f"💰 *Place Bet*\n\n"
            f"*Market:* {market['question']}\n"
            f"*Side:* {side_emoji}\n\n"
            f"Enter the amount in MON you want to bet.\n\n"
            f"Example: `10` or `25.50`",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Error: {str(e)}", show_alert=True)


@router.message(PlaceBetStates.entering_amount)
async def process_bet_amount(message: Message, state: FSMContext):
    """Process bet amount"""
    try:
        amount = float(message.text.strip())
        
        # Validate amount
        if amount <= 0:
            await message.answer(
                "❌ Amount must be greater than 0.",
                parse_mode="Markdown"
            )
            return
        
        if amount > 1000000:
            await message.answer(
                "❌ Amount too large. Maximum bet is 1,000,000 MON.",
                parse_mode="Markdown"
            )
            return
        
        # Save amount
        await state.update_data(amount=amount)
        await state.set_state(PlaceBetStates.confirming_bet)
        
        # Get saved data
        data = await state.get_data()
        question = data['question']
        side = data['side']
        side_bool = data['side_bool']
        market_id = data['market_id']
        side_emoji = "✅ YES" if side == "yes" else "❌ NO"
        
        # Get market data to calculate profit/loss
        blockchain = BlockchainService()
        market = await blockchain.get_market(market_id)
        
        current_yes = blockchain.parse_mon_amount(market['total_yes'])
        current_no = blockchain.parse_mon_amount(market['total_no'])
        
        # Calculate new pools after bet
        new_yes = current_yes + (amount if side_bool else 0)
        new_no = current_no + (amount if not side_bool else 0)
        total_pool = new_yes + new_no
        
        # Calculate potential payout and profit
        if side_bool:  # Betting YES
            # If YES wins, you get (total_pool * your_share_of_yes_pool)
            your_share = amount / new_yes if new_yes > 0 else 0
            potential_payout = total_pool * your_share
        else:  # Betting NO
            your_share = amount / new_no if new_no > 0 else 0
            potential_payout = total_pool * your_share
        
        profit = potential_payout - amount
        profit_percent = (profit / amount * 100) if amount > 0 else 0
        
        # Format profit/loss display
        if profit > 0:
            profit_emoji = "📈"
            profit_text = f"+{profit:.2f} MON (+{profit_percent:.1f}%)"
        elif profit < 0:
            profit_emoji = "📉"
            profit_text = f"{profit:.2f} MON ({profit_percent:.1f}%)"
        else:
            profit_emoji = "➖"
            profit_text = "0.00 MON (0%)"
        
        # Show confirmation
        confirmation_text = (
            "📋 *Confirm Bet*\n\n"
            f"*Market:* {question}\n"
            f"*Side:* {side_emoji}\n"
            f"*Amount:* {amount:.2f} MON\n\n"
            f"💰 *Potential Returns (if you win):*\n"
            f"  • Payout: {potential_payout:.2f} MON\n"
            f"  • Profit: {profit_emoji} {profit_text}\n\n"
            "⚠️ This will:\n"
            "1. Approve MON spending\n"
            "2. Place your bet on-chain\n\n"
            "Proceed?"
        )
        
        await message.answer(
            confirmation_text,
            reply_markup=get_confirmation_keyboard("confirm_place_bet"),
            parse_mode="Markdown"
        )
        
    except ValueError:
        await message.answer(
            "❌ Invalid amount. Please enter a number.\n\n"
            "Example: `10` or `25.50`",
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "confirm_place_bet", PlaceBetStates.confirming_bet)
async def confirm_place_bet(callback: CallbackQuery, state: FSMContext):
    """Confirm and execute bet placement"""
    await callback.answer("Processing bet...")
    
    # Get saved data
    data = await state.get_data()
    market_id = data['market_id']
    side_bool = data['side_bool']
    amount = data['amount']
    question = data['question']
    side = data['side']
    
    try:
        blockchain = BlockchainService()
        
        # Convert amount to token units
        amount_wei = blockchain.format_mon_amount(amount)
        
        # Step 1: Approve USDC
        await callback.message.edit_text(
            "⏳ *Step 1/2: Approving MON...*\n\n"
            "Please wait while we approve the token spending.",
            parse_mode="Markdown"
        )
        
        approve_tx = await blockchain.approve_mon(amount_wei)
        
        # Step 2: Place bet
        await callback.message.edit_text(
            "⏳ *Step 2/2: Placing bet...*\n\n"
            "Submitting your bet to the blockchain.",
            parse_mode="Markdown"
        )
        
        bet_tx = await blockchain.place_bet(market_id, side_bool, amount_wei)
        
        # Get updated market data
        updated_market = await blockchain.get_market(market_id)
        total_yes = blockchain.parse_mon_amount(updated_market['total_yes'])
        total_no = blockchain.parse_mon_amount(updated_market['total_no'])
        
        # Clear state
        await state.clear()
        
        side_emoji = "✅ YES" if side == "yes" else "❌ NO"
        
        # Show success message with updated pools
        success_text = (
            "✅ *Bet Placed Successfully!*\n\n"
            f"*Market:* {question}\n"
            f"*Side:* {side_emoji}\n"
            f"*Amount:* {amount:.2f} MON\n\n"
            f"*Updated Pools:*\n"
            f"  ✅ YES: {total_yes:.2f} MON\n"
            f"  ❌ NO: {total_no:.2f} MON\n\n"
            f"*Transaction Hash:*\n`{bet_tx}`"
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await state.clear()
        
        error_text = (
            "❌ *Bet Placement Failed*\n\n"
            f"Error: {str(e)}\n\n"
            "Please check:\n"
            "• You have sufficient MON balance\n"
            "• The market is still active\n"
            "• Your wallet has enough gas"
        )
        
        await callback.message.edit_text(
            error_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
