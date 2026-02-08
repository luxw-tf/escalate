"""
Start command handler
Displays main menu and handles navigation
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    # Clear any existing state
    await state.clear()
    
    welcome_text = (
        "🎯 *Welcome to Escalate*\n\n"
        "A decentralized prediction market on Monad testnet.\n\n"
        "Choose an option below to get started:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Handle back to menu button"""
    # Clear any existing state
    await state.clear()
    
    welcome_text = (
        "🎯 *Escalate - Main Menu*\n\n"
        "Choose an option below:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Handle cancel button"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Action cancelled.\n\nReturning to main menu...",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
