import requests
from io import BytesIO

from environs import Env


def get_products(strapi_api_token):
    products_url = 'http://localhost:1337/api/products'

    headers = {'Authorization': f'Bearer {strapi_api_token}'}

    response = requests.get(products_url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product(strapi_api_token, product_id):
    product_url = f'http://localhost:1337/api/products/{product_id}'
    params = {
        'populate': '*'
    }
    headers = {'Authorization': f'Bearer {strapi_api_token}'}

    product = requests.get(product_url, params=params, headers=headers)
    product.raise_for_status()
    img_url = product.json()['data']['picture'][0]['url']
    image_link = f'http://localhost:1337/{img_url}'
    img_responce = requests.get(image_link)
    img_responce.raise_for_status()
    image_data = BytesIO(img_responce.content)
    
    return product.json()['data'], image_data


def get_cart_by_id(strapi_api_token, user_id):
    url = 'http://localhost:1337/api/carts'
    params = {
        'filters[tg_id][$eq]': user_id,
        'populate': '*'
    }
    headers = {
        'Authorization': f'Bearer {strapi_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()['data'][0]['cart_products']


def get_or_create_cart(strapi_api_token, user_id):
    url = 'http://localhost:1337/api/carts'
    params = {
        'filters[tg_id][$eq]': user_id
    }
    headers = {
        'Authorization': f'Bearer {strapi_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    if len(response.json()['data']) == 0:
        url = 'http://localhost:1337/api/carts'
        headers = {
            'Authorization': f'Bearer {strapi_api_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'data': {
                'tg_id': user_id,
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    return response.json()['data'][0]['documentId']


def create_cart_product(strapi_api_token, product_id, quantity=1):
    url_post = f'http://localhost:1337/api/cart-products'
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }
    data = {
        'data': {
            'product': {
                'connect': product_id
            },
            'quantity': quantity,
        }
    }
    response = requests.post(url_post, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_cart_product(strapi_api_token, cart_product_id):
    url_post = f'http://localhost:1337/api/cart-products/{cart_product_id}'
    params = {
        'populate': '*'
    }
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }
    
    response = requests.get(url_post, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def add_cart_product_to_cart(strapi_api_token, cart_id, cart_product_id):
    url_put = f'http://localhost:1337/api/carts/{cart_id}'
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }
    data = {
        "data": {
            "cart_products": {
                "connect": [cart_product_id],
            },
        }
    }
    response = requests.put(url_put, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    strapi_api_token = env('STRAPI_API_TOKEN')
    user_id = '1011004829'
    cart_products = get_cart_by_id(strapi_api_token, user_id)
    for cart_product in cart_products:
        cart_product_id = cart_product['documentId']
        print(get_cart_product(strapi_api_token, cart_product_id))