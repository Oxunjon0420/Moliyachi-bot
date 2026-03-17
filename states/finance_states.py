"""
FSM states for all conversation flows.
"""
from aiogram.fsm.state import State, StatesGroup


class AddExpenseStates(StatesGroup):
    waiting_amount      = State()
    waiting_category    = State()
    waiting_description = State()


class AddIncomeStates(StatesGroup):
    waiting_amount      = State()
    waiting_category    = State()
    waiting_description = State()


class EditTransactionStates(StatesGroup):
    waiting_tx_id     = State()   # user types the ID
    waiting_field     = State()   # choose field to edit
    waiting_new_value = State()   # type new value


class DeleteTransactionStates(StatesGroup):
    confirm = State()


class AiAdvisorStates(StatesGroup):
    chatting = State()