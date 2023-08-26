import asyncio
from datetime import datetime as dt
from random import choice
from typing import Union

import aiohttp
from playwright._impl._browser import Browser
from playwright._impl._page import Page
from playwright.async_api import async_playwright
from playwright.async_api._generated import Playwright as AsyncPlaywright

from config import (GLOBAL_RETRIES, HEADLESS, PAGE_RETRIES,
                    PROXY_LOGIN, PROXY_PASS, PROXY_SITE, USER_AGENTS,
                    WAIT_AFTER_CART, WAIT_AFTER_FINISH)
from xpath_conf import (ITEM_MAIN_PAGE, NEXT_PAGE, OPTIONS, PAGE_HEIGHT,
                        RECOMMENDATIONS, SEARCH_BLOCK, SEARCH_RESULTS)


async def init_browser(pw: AsyncPlaywright, proxy: tuple = None) -> Browser:
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
            proxy={
                "server": f'http://{proxy[0]}:{proxy[1]}',
                "username": PROXY_LOGIN,
                "password": PROXY_PASS
            },
            args=args,
            headless=HEADLESS
        )
    else:
        browser = await pw.chromium.launch(
            args=args,
            headless=HEADLESS
        )
    return browser


async def get_proxies():
    async with aiohttp.ClientSession() as session:
        async with session.get(PROXY_SITE) as response:
            j = await response.json()
            proxies = [
                (j['list'][i]['ip'], j['list'][i]['port']) for i in j['list']
            ]
    return proxies


async def perform_search(
        page: Page, prompt: str, color: str, task_id: int) -> bool:
    try:
        search_box = page.locator(f"xpath={SEARCH_BLOCK}")
        await asyncio.sleep(2)
        await search_box.click()
        await asyncio.sleep(2)
        await search_box.type(prompt, delay=200, timeout=20000)
        await asyncio.sleep(2)
        await search_box.press('Enter')
        page.get_by_text('По запросу')
        await asyncio.sleep(2)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Результаты поиска: ОК'
        )
        return True
    except Exception as ex:
        print(ex)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Результаты: Ошибка - {type(ex).__name__}')
        return False


async def smooth_scroll(page: Page, location_y: int) -> None:
    for i in range(1, location_y, 5):
        await page.evaluate(f'window.scrollTo(0, {i});')
    await asyncio.sleep(2)


async def find_item(page: Page, item_id: int) -> None:
    item = page.locator(f'#c{item_id}')
    await item.hover(timeout=5000)
    await asyncio.sleep(2)
    await item.click()
    await asyncio.sleep(2)


async def add_to_cart(
        color: str, page: Page, task_id: int) -> bool:
    await asyncio.sleep(3)
    try:
        cart = page.get_by_role('button', name='Добавить в корзину')
        await cart.click()
        await asyncio.sleep(WAIT_AFTER_CART)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Корзина: ОК'
        )
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
        color: str, page: Page, task_id: int, item_id: int) -> bool:
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
        return True
    except Exception as ex:
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Товар с id {item_id} не найден'
        )
        return False
    

async def return_to_first_page(
        color: str, page: Page, task_id: int):
    print(
        color + f'{dt.now().strftime("%H:%M:%S")} |',
        f'Задача {task_id} |',
        'Возврат на первую страницу'
    )
    try:
        first_page = page.locator(
            'a.pagination-item.pagination__item.j-page', has_text='1')
        await first_page.hover()
        await asyncio.sleep(2)
        await first_page.click()
    except:
        pass
    return True


async def click_random_item(
        color: str, page: Page, task_id: int):
    try:
        await asyncio.sleep(5)
        attempts = 7
        while attempts:
            item = page.locator(ITEM_MAIN_PAGE.format(choice(range(1, 6))))
            attr = await item.get_attribute('class')
            if 'product-card--adv' in attr:
                attempts -= 1
                continue
            await item.hover()
            await asyncio.sleep(5)
            await item.click()
            break

        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            f'Выбран товар {await item.get_attribute("data-nm-id")}'
        )
        await asyncio.sleep(10)
    except Exception as ex:
        print(ex)
    return True


async def open_site(
        color: str, browser: Browser, task_id: int) -> Union[Page, None]:
    try:
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto("https://www.wildberries.ru")
        page.set_default_timeout(3000)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Сайт: ОК'
        )
        return page
    except Exception as ex:
        print(ex)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Сайт: Ошибка'
        )
        return None


async def click_recommendations(
        color: str, page: Page, task_id: int):
    await asyncio.sleep(5)
    try:
        await smooth_scroll(page, PAGE_HEIGHT)
        item = page.locator(RECOMMENDATIONS)
        await item.hover()
        await asyncio.sleep(2)
        await item.click()
        await page.wait_for_load_state()
        await asyncio.sleep(10)
        print(
            color + f'{dt.now().strftime("%H:%M:%S")} |',
            f'Задача {task_id} |',
            'Выбраны рекомендации'
        )
    except Exception as ex:
        print(ex)


async def select_options(
        color: str, page: Page, task_id: int):
    await asyncio.sleep(5)
    try:
        option = page.locator(OPTIONS).first
        await option.click()
        await asyncio.sleep(2)
    except Exception:
        pass


async def wildberries(task: tuple, color: str) -> bool:
    print(
        color + f'{dt.now().strftime("%H:%M:%S")} |',
        f'Запуск задачи: {task}'
    )
    task_id, prompt, item_id, operations, add_to_cart_rate = task
    global_retries = GLOBAL_RETRIES

    async with async_playwright() as pw:
        proxies = await get_proxies()
        percent_counter = add_to_cart_rate
        while operations and global_retries:
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

            search_ok = await perform_search(page, prompt, color, task_id)
            if not search_ok:
                await browser.close()
                continue

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
                    await smooth_scroll(page, PAGE_HEIGHT)
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

            if not percent_counter:
                await select_options(color, page, task_id)
                cart_ok = await add_to_cart(color, page, task_id)
                percent_counter = add_to_cart_rate
                await page.go_back()
                await return_to_first_page(color, page, task_id)
                await smooth_scroll(page, 3000)
                await click_random_item(color, page, task_id)
                await select_options(color, page, task_id)
                await add_to_cart(color, page, task_id)
            else:
                await click_recommendations(color, page, task_id)
                cart_ok = True
                percent_counter -= 1
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
            await asyncio.sleep(WAIT_AFTER_FINISH)
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
