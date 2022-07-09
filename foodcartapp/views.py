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
        fields = ['product']


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderingProductSerializer(), allow_empty=False)
    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    

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

    serializer = OrderSerializer(data=product_order)
    serializer.is_valid(raise_exception=True)

    print(repr(OrderSerializer()))
    
    order = Order.objects.create(
        name=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phone_number=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
        )

    for product in serializer.validated_data['products']:
        ordering_product = Product.objects.get(id=product['product'])
        OrderingProduct.objects.create(
            order=order,
            product=ordering_product,
            quantity=product['quantity']
        )
    
    return JsonResponse({})
