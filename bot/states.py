"""
FSM States for Escalate Bot
Defines all conversation states for different flows
"""
from aiogram.fsm.state import State, StatesGroup


class CreateMarketStates(StatesGroup):
    """States for creating a new market"""
    entering_question = State()
    entering_expiry = State()
    confirming = State()


class PlaceBetStates(StatesGroup):
    """States for placing a bet"""
    selecting_market = State()
    selecting_side = State()
    entering_amount = State()
    confirming_bet = State()


class ResolveMarketStates(StatesGroup):
    """States for resolving a market"""
    entering_market_id = State()
    entering_outcome = State()
    confirming_resolution = State()
