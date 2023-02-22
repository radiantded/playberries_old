from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


all_tasks = KeyboardButton('💡 Все задачи')
launch_task = KeyboardButton('⚙️ Запустить задачу')
new_task = KeyboardButton('➕ Создать задачу')
delete_task = KeyboardButton('❌ Удалить задачу')

launch = KeyboardButton('✅ Запустить')
cancel = KeyboardButton('❌ Отмена')

start_kb = ReplyKeyboardMarkup(
    resize_keyboard=True
).row(
    all_tasks,
    launch_task
).row(
    new_task,
    delete_task
)

launch_que_kb = ReplyKeyboardMarkup(
    resize_keyboard=True
).add(
    launch,
    cancel
)

cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True
).add(cancel)
