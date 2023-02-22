from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateTaskFSM(StatesGroup):
    create = State()
    
class CreateQueFSM(StatesGroup):
    que = State()
    finish = State()

class DeleteTaskFSM(StatesGroup):
    delete = State()
