from random import choice

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import Message
from aiogram.utils.executor import start_polling

from config import AUTH_USERS, BOT_TOKEN, CONSOLE_COLORS
from db import Database
from keyboards import cancel_kb, launch_que_kb, start_kb
from playberries import wildberries
from sfms import CreateQueFSM, CreateTaskFSM, DeleteTaskFSM


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


async def make_reply(db_data: tuple) -> str:
    if not db_data:
        reply = '❌ Нет задач!'
    else:
        tasks = []
        for t in db_data:
            string = (
                f'🔸 id: {t[0]} | Запрос: {t[1]} |'
                f'Артикул: {t[2]} | Повторов: {t[3]}'
            )
            tasks.append(string)
            delimeter = '\n' + ('-' * 90) +'\n'
            reply = delimeter.join(tasks)
    return reply


@dp.message_handler(state=CreateQueFSM.que)
async def register_tasks(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    elif message.text == '❌ Отмена':
        await state.finish()
        await message.answer(
            f'❌ Операция отменена',
            reply_markup=start_kb
        )
    else:
        task_id = message.text
        try:
            async with Database() as base:
                task = await base.get_one(task_id)
        except Exception as ex:
            await message.answer(
                '❌ Неверный ввод',
                reply_markup=cancel_kb)
        if not task:
            await message.answer(
                '❌ Нет задач с таким id',
                reply_markup=cancel_kb)
        else:
            async with state.proxy() as data:
                data['que'] = task
            await message.answer(
                f'✅ Задача {message.text} готова к запуску',
                reply_markup=launch_que_kb
            )
            await message.answer('⚙️ Подтвердите запуск задачи')
            await CreateQueFSM.next()
    

@dp.message_handler(state=DeleteTaskFSM.delete)
async def register_tasks(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    elif message.text == '❌ Отмена':
        await state.finish()
        await message.answer(
            f'❌ Операция отменена',
            reply_markup=start_kb
        )
    else:
        task = message.text
        async with Database() as base:
            await base.delete(task)
        await state.finish()
        await message.answer(
            f'✅ Задача {task} удалена',
            reply_markup=start_kb
        )


@dp.message_handler(state=CreateQueFSM.finish)
async def que_handler(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    else:
        async with state.proxy() as data:
            task = data['que']
            if message.text == '❌ Отмена':
                await state.finish()
                await message.answer(
                    f'❌ Запуск задачи {task} отменён',
                    reply_markup=start_kb
                )
            elif message.text == '✅ Запустить':
                await message.answer(
                    f'🚀 Задача {task} запущена', 
                    reply_markup=start_kb)
                await state.finish()
                result = await wildberries(task, choice(CONSOLE_COLORS))
                if not result:
                    await message.answer(
                        f'❌ Задача {task} завершилась с ошибкой',
                        reply_markup=start_kb
                    )
                else:    
                    await message.answer(
                        f'✅ Задача {task} успешно завершена',
                        reply_markup=start_kb
                    )
            
    
@dp.message_handler(state=CreateTaskFSM.create)
async def create_task(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён') 
    elif message.text == '❌ Отмена':
        await state.finish()
        await message.answer(
            f'❌ Операция отменена',
            reply_markup=start_kb
        )
    else:
        task = message.text.split(', ')
        if len(task) != 3:
            await message.answer('❌ Некорректный ввод')
        else:
            async with Database() as base:
                await base.add(tuple(task))
            await message.answer(
                f'✅ Задача {task} добавлена в базу данных',
                reply_markup=start_kb
            )
            await state.finish()


@dp.message_handler(text='💡 Все задачи')
async def get_all_tasks(message: Message):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    else:
        async with Database() as base:
            db_data = await base.get_all()
        reply = await make_reply(db_data)
        await message.answer(
            reply, 
            reply_markup=start_kb
        )
    

@dp.message_handler(text='➕ Создать задачу')
async def get_task_params(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')   
    else: 
        await message.answer(
            ('⚙️ Введите параметры задачи: <поисковый запрос>, '
             '<артикул>, <количество повторов>')
        )
        await message.answer(
            '⚙️ Пример: iPhone, 1234567, 100',
            reply_markup=cancel_kb
        )
        await CreateTaskFSM.create.set()


@dp.message_handler(text='❌ Удалить задачу')
async def delete_task(message: Message, state: FSMContext):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    else:
        await message.answer(
            '⚙️ Введите id задачи для удаления',
            reply_markup=cancel_kb
        )
        await DeleteTaskFSM.delete.set()



@dp.message_handler(text='⚙️ Запустить задачу')
async def create_que(message: Message):
    await message.delete()
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')    
    await message.answer(
        '⚙️ Введите id задачи для запуска',
        reply_markup=cancel_kb
    )
    await CreateQueFSM.que.set()


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.delete()
    print(message.from_id)
    if not message.from_id in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
    else:
        await message.answer(
            '☀️ Добро пожаловать!',
            reply_markup=start_kb
        )


if __name__ == "__main__":
    start_polling(dp, timeout=10000, skip_updates=True)
