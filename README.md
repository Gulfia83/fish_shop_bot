# FISH_SHOP_BOT

Бот онлайн магазина продажи морепродуктов

## Установка
1. Установите Python и создайте виртуальное окружение, активируйте его.

2. Установите необходимые зависимости с помощью `pip`:
    ```sh
    pip install -r requirements.txt

## Установка Strapi

Node.js должен быть установлен на компьютере.
Установите Strapi
```sh
npx create-strapi@latest
```
Перейдите в директорию проекта strapi и настройте админ-панель
```sh
npm run build
```
В админ-панели нужно создать следующие модели:
1. Product с полями title, description, picture, price
2. Cart с полями tg_id
3. CartProduct с полями quantity и связать ее с моделями Product и Cart
4. Client с полями tg_id, email и связать с моделью Cart

## Переменные окружения

Создайте файл `.env` и поместите в него следующие переменные окружения:
    ```env
    TG_BOT_TOKEN='токен телеграм бота' - получить у [BotFather]('@BotFather')
    REDIS_DB_HOST='адрес хоста вашего сервера базы данных Redis' ('localhost')
    REDIS_DB_PORT='номер порта сервера базы данных Redis' ('6379')
    STRAPI_API_TOKEN='токен API сервера Strapi' - получить в настройках админ панели Strapi
    STRAPI_URL='адрес Strapi сервера'. По умолчанию 'http://localhost:1337'
    ```
## Запуск

Запустите redis сервер

```sh
cd ./redis
redis-server.exe
```
Запустите Strapi проект

```sh
npm run develop
```
Запустите бота
```sh
python tg_bot.py
```
## Пример работы бота

[fish_shop_bot](https://github.com/user-attachments/assets/84e4e9d1-2372-49e9-9d0c-5ed1cbcc4a78)
