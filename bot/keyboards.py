"""
Inline keyboards for Escalate Bot
Provides Polymarket-style interactive keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📊 View Markets", callback_data="view_markets")],
        [InlineKeyboardButton(text="➕ Create Market", callback_data="create_market")],
        [InlineKeyboardButton(text="💰 Place Bet", callback_data="place_bet")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_market_list_keyboard(markets: List[Dict]) -> InlineKeyboardMarkup:
    """
    Get keyboard for market listing
    
    Args:
        markets: List of market dictionaries
    """
    keyboard = []
    
    for market in markets:
        market_id = market['id']
        # Add market row with bet buttons
        keyboard.append([
            InlineKeyboardButton(
                text=f"📈 Market #{market_id}",
                callback_data=f"view_market_{market_id}"
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text="✅ Bet YES",
                callback_data=f"bet_yes_{market_id}"
            ),
            InlineKeyboardButton(
                text="❌ Bet NO",
                callback_data=f"bet_no_{market_id}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_market_detail_keyboard(market_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for individual market details"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Bet YES",
                callback_data=f"bet_yes_{market_id}"
            ),
            InlineKeyboardButton(
                text="❌ Bet NO",
                callback_data=f"bet_no_{market_id}"
            )
        ],
        [InlineKeyboardButton(text="🔙 Back to Markets", callback_data="view_markets")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_side_selection_keyboard(market_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for selecting bet side"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ YES",
                callback_data=f"side_yes_{market_id}"
            ),
            InlineKeyboardButton(
                text="❌ NO",
                callback_data=f"side_no_{market_id}"
            )
        ],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_outcome_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting resolution outcome"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ YES", callback_data="outcome_yes"),
            InlineKeyboardButton(text="❌ NO", callback_data="outcome_no")
        ],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get simple cancel keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
