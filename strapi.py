import requests
from io import BytesIO


def get_products(strapi_api_token, strapi_url):
    products_url = f'{strapi_url}/api/products'

    headers = {'Authorization': f'Bearer {strapi_api_token}'}

    response = requests.get(products_url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product(strapi_api_token, strapi_url, product_id):
    product_url = f'{strapi_url}/api/products/{product_id}'
    params = {
        'populate': '*'
    }
    headers = {'Authorization': f'Bearer {strapi_api_token}'}

    product = requests.get(product_url, params=params, headers=headers)
    product.raise_for_status()
    img_url = product.json()['data']['picture'][0]['url']
    image_link = f'{strapi_url}/{img_url}'
    img_responce = requests.get(image_link)
    img_responce.raise_for_status()
    image_data = BytesIO(img_responce.content)
    
    return product.json()['data'], image_data


def get_cart_by_id(strapi_api_token, strapi_url, user_id):
    url = f'{strapi_url}/api/carts'
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
    return response.json()['data'][0]


def create_cart(strapi_api_token, strapi_url, user_id):
    url = f'{strapi_url}/api/carts'
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


def create_cart_product(strapi_api_token, strapi_url, product_id, quantity=1):
    url_post = f'{strapi_url}/api/cart-products'
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


def get_cart_product(strapi_api_token, strapi_url, cart_product_id):
    url_post = f'{strapi_url}/api/cart-products/{cart_product_id}'
    params = {
        'populate': '*'
    }
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }

    response = requests.get(url_post, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def delete_cart_product(strapi_api_token, strapi_url, cart_product_id):
    url = f'{strapi_url}/api/cart-products/{cart_product_id}'
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_cart_product_to_cart(strapi_api_token,
                             strapi_url,
                             cart_id,
                             cart_product_id):
    url_put = f'{strapi_url}/api/carts/{cart_id}'
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }
    data = {
        'data': {
            'cart_products': {
                'connect': [cart_product_id],
            },
        }
    }
    response = requests.put(url_put, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_client(strapi_api_token,
               strapi_url,
               user_id):
    url = f'{strapi_url}/api/clients'
    params = {
        'filters[tg_id][$eq]': user_id
    }
    headers = {
        'Authorization': f'Bearer {strapi_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()


def create_client(strapi_api_token,
                  strapi_url,
                  user_id,
                  email,
                  cart_id):
    url = f'{strapi_url}/api/clients'
    headers = {
        'Authorization': f'bearer {strapi_api_token}',
    }

    data = {
        'data': {
            'email': email,
            'tg_id': user_id,
            'carts': {
                'connect': [cart_id],
            },
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
