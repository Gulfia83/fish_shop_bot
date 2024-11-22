# FISH_SHOP_BOT

Бот онлайн магазина продажи морепродуктов

## Пример работы бота

[fish_shop_bot](https://github.com/user-attachments/assets/84e4e9d1-2372-49e9-9d0c-5ed1cbcc4a78)

## Установка
1. Установите Python и создайте виртуальное окружение, активируйте его:

2. Установите необходимые зависимости с помощью `pip`:
    ```sh
    pip install -r requirements.txt

3. Этот проект использует базу данных Redis. Создайте и подключите ваш экземпляр на [redis website](https://app.redislabs.com/)
4. Получите токен для вашего телеграм-бота и для вашего сообщества в ВК.
5. Создайте файл `.env` и поместите в него следующие переменные окружения:
    ```env
    TG_BOT_TOKEN='токен телеграм бота'
    REDIS_DB_HOST='адрес хоста вашего сервера базы данных Redis'
    REDIS_DB_PORT='номер порта сервера базы данных Redis'
    STRAPI_API_TOKEN='токен API сервера Strapi'
    ```
6. Запустите redis сервер

7. Запустите Strapi проект

```sh
npm run develop
```
8. Запустите бота
```sh
python tg_bot.py
```
