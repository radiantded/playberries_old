import asyncio
import time
from datetime import datetime as dt
from random import choice
from typing import Union

from playwright._impl._browser import Browser
from playwright._impl._locator import Locator
from playwright.async_api import async_playwright
from playwright.async_api._generated import Playwright as AsyncPlaywright

from config import OPTIONS_RETRIES, PAGE_RETRIES, PROXY_SITE, USER_AGENTS
from xpath_conf import (CARTS, COLORS, NEXT_PAGE, OPTIONS, PAGE_HEIGHT,
                        SEARCH_BLOCK, SEARCH_RESULTS)


async def init_browser(pw: AsyncPlaywright, proxy: tuple=None) -> Browser:
    user_agent = choice(USER_AGENTS)
    args = [
        f'--user-agent={user_agent}',
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--window-size=1920,1080"
    ]
    if proxy:
        print(
            f'{dt.now().strftime("%H:%M:%S")} |',
            f'Подключение через прокси: {proxy}'
        )
        browser = await pw.chromium.launch(
            proxy={"server": f'http://{proxy}'},
            args=args
        )
    else:
        browser = await pw.chromium.launch(args=args, headless=True)
    return browser
        

async def get_proxies(browser: Browser) -> tuple:
    page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
    await page.goto(PROXY_SITE)
    text = await page.inner_text('body')
    proxies = tuple(text.split('\n'))
    print(
        f'{dt.now().strftime("%H:%M:%S")} |',
        f'Доступных прокси: {len(proxies)}'
    )
    await browser.close()
    return proxies


async def perform_search(
    page: Locator, prompt: str, color: str, task_id: int) -> bool:
    try:
        search_box = page.locator(f"xpath={SEARCH_BLOCK}")
        await asyncio.sleep(2)
        await search_box.click()
        await asyncio.sleep(2)
        await search_box.type(prompt, delay=200)
        await asyncio.sleep(2)
        await search_box.press('Enter')
        await page.locator(f"xpath={SEARCH_RESULTS}").is_enabled()
        await asyncio.sleep(2)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Результаты поиска: ОК'
        )
        return True
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Результаты: Ошибка - {type(ex).__name__}')
        return False


async def smooth_scroll(page: Locator, location_y: int) -> None:
    for i in range(1, location_y, 10):
        await page.evaluate(f'window.scrollTo(0, {i});')
    await asyncio.sleep(2)
            
            
async def find_item(page: Locator, item_id: int) -> None:
    item = page.locator(f'#c{item_id}')
    await item.is_enabled(timeout=20000)
    await item.hover(timeout=20000)
    await asyncio.sleep(2)
    await item.click()
    await asyncio.sleep(2)
    
    
async def add_to_cart(
    color: str, page: Locator, task_id: int, cart_path: str) -> bool:
    try:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Корзина: ОК'
        )
        cart = page.locator(f"xpath={cart_path}")
        await cart.click()
        await asyncio.sleep(2)
        return True
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Корзина: Ошибка - {type(ex).__name__}'
        )
        await asyncio.sleep(1)
        return False


async def go_to_next_page(
    color: str, page: Locator, task_id: int, item_id: int) -> bool:
    try:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Переход на следующую страницу'
        )
        next_page = page.locator(f'css={NEXT_PAGE}')
        await next_page.hover()
        await asyncio.sleep(2)
        await next_page.click()
        await asyncio.sleep(5)
        return True
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Товар с id {item_id} не найден'
        )
        return False
    

async def refresh_proxies(
    color: str, task_id: int, pw: AsyncPlaywright) -> tuple[str]:
    try:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Обновляем прокси'
        )
        browser = await init_browser(pw, proxy=None)
        proxies = await get_proxies(browser)
        return proxies
    except Exception as ex:
        print(color + ex.__str__()) 
        return None


async def open_site(
    color: str, browser: Browser, task_id: int) -> Union[Locator, None]:
    try:
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto("https://www.wildberries.ru")
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Сайт: ОК'
        )
        return page
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Сайт: Ошибка'
        )
        return None
    

async def check_colors(
    color: str, page: Locator, task_id: int, operations: int) -> bool:
    try:
        await page.locator(f"xpath={COLORS}").is_visible(timeout=60000)
        await asyncio.sleep(10)
        return True
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Страница товара: Ошибка - {type(ex).__name__}'
        )
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Перезапуск цикла, осталось циклов: {operations}'
        )
        return False


async def wildberries(task: tuple, color: str) -> bool:
    print(
        color + f'{dt.now().strftime("%H:%M:%S")} |',
        f'Запуск задачи: {task}'
    )
    task_id, prompt, item_id, operations = task
    global_retries = 150
    
    async with async_playwright() as pw:
        proxies = await refresh_proxies(color, task_id, pw)
        timestamp = time.perf_counter()
        
        while operations and global_retries:
            current_time = time.perf_counter()
            if current_time - timestamp >= 300:
                proxies = await refresh_proxies(color, task_id, pw)
                timestamp = current_time
            if not proxies:
                print(
                    color + f'{dt.now().strftime("%H:%M:%S")} |',
                    'Ошибка получения прокси'
                )
                return False
            browser = await init_browser(pw, proxy=choice(proxies))
            
            page = await open_site(color, browser, task_id)
            if not page:
                await browser.close()
                continue
            await asyncio.sleep(2)
            
            search_ok = await perform_search(page, prompt, color, task_id)
            if not search_ok:
                await browser.close()
                continue
            await asyncio.sleep(5)
            
            item_page_ok = False
            for p in range(1, PAGE_RETRIES):
                try:
                    print(
                        color + f'{dt.now().strftime("%H:%M:%S")} |',
                        f'Задача {task_id} |',
                        f'Страница {p}'
                    )
                    await page.locator(
                        f"xpath={SEARCH_RESULTS}").is_enabled(timeout=60000)
                    await asyncio.sleep(2)
                    await smooth_scroll(page, PAGE_HEIGHT)
                    await asyncio.sleep(2)
                    await find_item(page, item_id)
                    item_page_ok = True
                    print(
                        color + f'{dt.now().strftime("%H:%M:%S")} |',
                        f'Задача {task_id} |',
                        'Товар: ОК'
                    )
                    break
                except Exception as ex:
                    next_page = await go_to_next_page(
                        color, page,
                        task_id, item_id
                    )
                    if not next_page:
                        await browser.close()
                        break
            if not item_page_ok:
                print(
                    color + f'{dt.now().strftime("%H:%M:%S")} |',
                    f'Задача {task_id} |',
                    f'Перезапуск цикла, осталось циклов: {operations}'
                )
                global_retries -= 1
                await browser.close()
                continue
            
            colors_ok = await check_colors(
                color, page,
                task_id, operations
            )
            if not colors_ok:
                await browser.close()
                continue
            
            cart_ok = False
            for o in range(1, OPTIONS_RETRIES):
                if not cart_ok:
                    try:
                        option = page.locator(f"xpath={OPTIONS.format(o)}")
                        await option.click()
                        await asyncio.sleep(2)
                        print(
                            color + f'{dt.now().strftime("%H:%M:%S")} |',
                            f'Задача {task_id} |',
                            f'Опция {o}'
                        )
                    except Exception as ex:
                        print(
                            color + f'{dt.now().strftime("%H:%M:%S")} |',
                            f'Задача {task_id} |',
                            f'Нет опций'
                        )
                    cart_ok = await add_to_cart(
                        color, page,
                        task_id, CARTS['1']
                    )
            if not cart_ok:
                print(
                    color + f'{dt.now().strftime("%H:%M:%S")} |',
                    f'Задача {task_id} |',
                    f'Перезапуск цикла, осталось циклов: {operations}'
                )
                await browser.close()
                global_retries -= 1
                continue
            else:
                print(
                    color + f'{dt.now().strftime("%H:%M:%S")} |',
                    f'Задача {task_id} |',
                    f'Цикл завершён, осталось циклов: {operations - 1}'
                )
                await browser.close()
                operations -= 1
            await asyncio.sleep(3)
            print(color + '-' * 50)
        if not global_retries:
            print(
                color + f'{dt.now().strftime("%H:%M:%S")} |',
                f'Достигнут лимит ошибок по задаче {task_id} '
            )
            return False
        elif not operations:
            print(
                color + f'{dt.now().strftime("%H:%M:%S")} |',
                f'Задача {task_id} завершена'
            )
            return True
