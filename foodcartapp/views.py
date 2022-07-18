from math import prod
from urllib import response
from django.http import JsonResponse
from django.templatetags.static import static
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField

from .models import Product, Order, OrderingProduct


class OrderingProductSerializer(ModelSerializer):
    class Meta:
        model = OrderingProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderingProductSerializer(), allow_empty=False, write_only=True)
    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']
    

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
    serializer = OrderSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    product_order = serializer.validated_data
    
    order = Order.objects.create(
        firstname=product_order['firstname'],
        lastname=product_order['lastname'],
        phonenumber=product_order['phonenumber'],
        address=product_order['address']
        )

    # for product in request.data['products']:
        
    #     ordering_product = Product.objects.get(id=product['product'])
    #     OrderingProduct.objects.create(
    #         order=order,
    #         product=ordering_product,
    #         quantity=product['quantity']
    #     )

    ordering_products = [
        OrderingProduct(
            product = product['product'],
            order = order,
            quantity = product['quantity'])
        for product in product_order['products']
    ]
    OrderingProduct.objects.bulk_create(ordering_products)

    
    return JsonResponse({})
