from urllib import response
from django.http import JsonResponse
from django.templatetags.static import static
import json

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Product, Order, OrderingProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):

    product_order = request.data

    if not product_order.get('products') \
        or not isinstance(product_order['products'], list):
            return Response({'error':'products key are not presented or not list'})

    
    if not product_order.get('firstname'):
        return Response({'error':'The key "firstname" is not specified or not str'})
    elif not product_order.get('lastname'):
        return Response({'error':'The key "lastname" is not specified or not str'})
    elif not product_order.get('phonenubmer'):
        return Response({'error':'The key "phonenumber" is not specified or not str'}) 
    elif not product_order.get('address'):
        return Response({'error':'The key "address" is not specified or not str'})


    order =Order.objects.create(
        name=product_order['firstname'],
        lastname=product_order['lastname'],
        phone_number=product_order['phonenumber'],
        address=product_order['address']
        )

    for product in product_order['products']:
        ordering_product = Product.objects.get(id=product['product'])
        OrderingProduct.objects.create(
            order=order,
            product=ordering_product,
            quantity=product['quantity']
        )
    
    return JsonResponse({})
