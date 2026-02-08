"""
Market resolution handlers
Allows resolver to resolve markets (resolver-only)
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import ResolveMarketStates
from bot.keyboards import get_outcome_keyboard, get_cancel_keyboard, get_main_menu_keyboard, get_confirmation_keyboard
from services.blockchain import BlockchainService
from config import Config

router = Router()


@router.message(Command("resolve"))
async def cmd_resolve(message: Message, state: FSMContext):
    """Handle /resolve command (resolver only)"""
    try:
        blockchain = BlockchainService()
        
        # Check if user is resolver
        if blockchain.wallet_address.lower() != Config.RESOLVER_ADDRESS.lower():
            await message.answer(
                "❌ *Access Denied*\n\n"
                "Only the designated resolver can resolve markets.",
                parse_mode="Markdown"
            )
            return
        
        await state.set_state(ResolveMarketStates.entering_market_id)
        
        await message.answer(
            "🏁 *Resolve Market*\n\n"
            "Enter the Market ID you want to resolve.\n\n"
            "Example: `1`",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Error: {str(e)}",
            parse_mode="Markdown"
        )


@router.message(ResolveMarketStates.entering_market_id)
async def process_market_id(message: Message, state: FSMContext):
    """Process market ID for resolution"""
    try:
        market_id = int(message.text.strip())
        
        if market_id <= 0:
            await message.answer(
                "❌ Invalid market ID. Please enter a positive number.",
                parse_mode="Markdown"
            )
            return
        
        # Fetch market
        blockchain = BlockchainService()
        market = await blockchain.get_market(market_id)
        
        if not market:
            await message.answer(
                f"❌ Market #{market_id} not found.",
                parse_mode="Markdown"
            )
            return
        
        if market['resolved']:
            await message.answer(
                f"❌ Market #{market_id} has already been resolved.",
                parse_mode="Markdown"
            )
            return
        
        # Save market data
        await state.update_data(
            market_id=market_id,
            question=market['question']
        )
        await state.set_state(ResolveMarketStates.entering_outcome)
        
        total_yes = blockchain.parse_mon_amount(market['total_yes'])
        total_no = blockchain.parse_mon_amount(market['total_no'])
        
        await message.answer(
            f"📊 *Market #{market_id}*\n\n"
            f"*Question:* {market['question']}\n\n"
            f"*Pools:*\n"
            f"  ✅ YES: {total_yes:.2f} MON\n"
            f"  ❌ NO: {total_no:.2f} MON\n\n"
            f"Select the outcome:",
            reply_markup=get_outcome_keyboard(),
            parse_mode="Markdown"
        )
        
    except ValueError:
        await message.answer(
            "❌ Invalid input. Please enter a number.\n\n"
            "Example: `1`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(
            f"❌ Error: {str(e)}",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("outcome_"), ResolveMarketStates.entering_outcome)
async def process_outcome(callback: CallbackQuery, state: FSMContext):
    """Process resolution outcome"""
    outcome = callback.data.split("_")[1]
    outcome_bool = (outcome == "yes")
    
    await state.update_data(outcome=outcome, outcome_bool=outcome_bool)
    await state.set_state(ResolveMarketStates.confirming_resolution)
    
    data = await state.get_data()
    market_id = data['market_id']
    question = data['question']
    
    outcome_emoji = "✅ YES" if outcome == "yes" else "❌ NO"
    
    confirmation_text = (
        "⚠️ *Confirm Market Resolution*\n\n"
        f"*Market ID:* #{market_id}\n"
        f"*Question:* {question}\n"
        f"*Outcome:* {outcome_emoji}\n\n"
        "This action is irreversible. Proceed?"
    )
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirmation_keyboard("confirm_resolve"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_resolve", ResolveMarketStates.confirming_resolution)
async def confirm_resolution(callback: CallbackQuery, state: FSMContext):
    """Confirm and execute market resolution"""
    await callback.answer("Resolving market...")
    
    data = await state.get_data()
    market_id = data['market_id']
    outcome_bool = data['outcome_bool']
    outcome = data['outcome']
    question = data['question']
    
    try:
        await callback.message.edit_text(
            "⏳ *Resolving market on blockchain...*\n\n"
            "Please wait.",
            parse_mode="Markdown"
        )
        
        blockchain = BlockchainService()
        tx_hash = await blockchain.resolve_market(market_id, outcome_bool)
        
        await state.clear()
        
        outcome_emoji = "✅ YES" if outcome == "yes" else "❌ NO"
        
        success_text = (
            "✅ *Market Resolved Successfully!*\n\n"
            f"*Market ID:* #{market_id}\n"
            f"*Question:* {question}\n"
            f"*Outcome:* {outcome_emoji}\n\n"
            f"*Transaction Hash:*\n`{tx_hash}`\n\n"
            "Winners can now claim their winnings."
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await state.clear()
        
        error_text = (
            "❌ *Resolution Failed*\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again or contact support."
        )
        
        await callback.message.edit_text(
            error_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
