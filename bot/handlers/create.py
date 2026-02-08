"""
Market creation handlers
Implements FSM flow for creating new prediction markets
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from bot.states import CreateMarketStates
from bot.keyboards import get_confirmation_keyboard, get_cancel_keyboard, get_main_menu_keyboard
from services.blockchain import BlockchainService
from config import Config

router = Router()


@router.callback_query(F.data == "create_market")
async def start_create_market(callback: CallbackQuery, state: FSMContext):
    """Start market creation flow"""
    await state.set_state(CreateMarketStates.entering_question)
    
    await callback.message.edit_text(
        "➕ *Create New Market*\n\n"
        "Please enter the market question.\n\n"
        "Example: _Will Bitcoin reach $100k by end of 2026?_",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(CreateMarketStates.entering_question)
async def process_question(message: Message, state: FSMContext):
    """Process market question"""
    question = message.text.strip()
    
    # Validate question
    if len(question) < 10:
        await message.answer(
            "❌ Question too short. Please enter at least 10 characters.",
            parse_mode="Markdown"
        )
        return
    
    if len(question) > 200:
        await message.answer(
            "❌ Question too long. Please keep it under 200 characters.",
            parse_mode="Markdown"
        )
        return
    
    # Save question
    await state.update_data(question=question)
    await state.set_state(CreateMarketStates.entering_expiry)
    
    await message.answer(
        f"✅ Question saved:\n_{question}_\n\n"
        f"Now enter the expiry date and time in UTC.\n\n"
        f"*Format:* `YYYY-MM-DD HH:MM`\n"
        f"*Example:* `2026-12-31 23:59`\n\n"
        f"_Minimum duration: {Config.MIN_MARKET_DURATION_MINUTES} minutes_",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )


@router.message(CreateMarketStates.entering_expiry)
async def process_expiry(message: Message, state: FSMContext):
    """Process market expiry"""
    expiry_str = message.text.strip()
    
    try:
        # Parse datetime
        expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M")
        expiry_timestamp = int(expiry_dt.timestamp())
        
        # Validate expiry
        now = int(datetime.utcnow().timestamp())
        min_expiry = now + (Config.MIN_MARKET_DURATION_MINUTES * 60)
        
        if expiry_timestamp <= min_expiry:
            await message.answer(
                f"❌ Expiry must be at least {Config.MIN_MARKET_DURATION_MINUTES} minutes in the future.\n\n"
                f"Please enter a valid expiry time.",
                parse_mode="Markdown"
            )
            return
        
        # Save expiry
        await state.update_data(expiry=expiry_timestamp, expiry_str=expiry_str)
        await state.set_state(CreateMarketStates.confirming)
        
        # Get saved data
        data = await state.get_data()
        question = data['question']
        
        # Show confirmation
        confirmation_text = (
            "📋 *Confirm Market Creation*\n\n"
            f"*Question:*\n{question}\n\n"
            f"*Expiry:* {expiry_str} UTC\n\n"
            "Proceed with creation?"
        )
        
        await message.answer(
            confirmation_text,
            reply_markup=get_confirmation_keyboard("confirm_create_market"),
            parse_mode="Markdown"
        )
        
    except ValueError:
        await message.answer(
            "❌ Invalid date format.\n\n"
            "Please use format: `YYYY-MM-DD HH:MM`\n"
            "Example: `2026-12-31 23:59`",
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "confirm_create_market", CreateMarketStates.confirming)
async def confirm_create_market(callback: CallbackQuery, state: FSMContext):
    """Confirm and execute market creation"""
    await callback.answer("Creating market...")
    
    # Get saved data
    data = await state.get_data()
    question = data['question']
    expiry = data['expiry']
    
    try:
        # Update message to show processing
        await callback.message.edit_text(
            "⏳ *Creating market on blockchain...*\n\n"
            "This may take a few moments. Please wait.",
            parse_mode="Markdown"
        )
        
        # Create market on blockchain
        blockchain = BlockchainService()
        tx_hash, market_id = await blockchain.create_market(question, expiry)
        
        # Clear state
        await state.clear()
        
        # Show success message
        success_text = (
            "✅ *Market Created Successfully!*\n\n"
            f"*Market ID:* #{market_id}\n"
            f"*Question:* {question}\n\n"
            f"*Transaction Hash:*\n`{tx_hash}`\n\n"
            "Your market is now live and accepting bets!"
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await state.clear()
        
        error_text = (
            "❌ *Market Creation Failed*\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again or contact support."
        )
        
        await callback.message.edit_text(
            error_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
