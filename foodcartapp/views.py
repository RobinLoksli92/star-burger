import requests
from django.http import JsonResponse
from django.templatetags.static import static
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField

from geo_location.models import GeoLocation

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


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    product_order = serializer.validated_data

    geo_location, is_created = GeoLocation.objects.get_or_create(
        address=product_order['address'],
    )

    if is_created:
        customer_coords = fetch_coordinates(settings.YANDEX_APIKEY, product_order['address'])
        if customer_coords:
            geo_location.long, geo_location.lat = customer_coords
            geo_location.save()

    order = Order.objects.create(
        firstname=product_order['firstname'],
        lastname=product_order['lastname'],
        phonenumber=product_order['phonenumber'],
        address=product_order['address'],
        geo_location=geo_location
    )

    ordering_products = [
        OrderingProduct(
            product = product['product'],
            order = order,
            quantity = product['quantity'],
            price=Product.objects.get(name=product['product']).price
        )
        for product in product_order['products']
    ]
    OrderingProduct.objects.bulk_create(ordering_products)
    
    return JsonResponse(serializer.data)
