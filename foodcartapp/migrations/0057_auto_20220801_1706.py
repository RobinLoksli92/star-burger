# Generated by Django 3.2 on 2022-08-01 15:06
from django.conf import settings
from django.db import migrations
import requests


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


def add_restaurants_coords(apps, scheme_editor):
    GeoLocation = apps.get_model('geo_location', 'GeoLocation')
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')
    for restaurant in Restaurant.objects.all():
        restaurant_coords = fetch_coordinates(settings.YANDEX_APIKEY, restaurant.address)
        restaurant_geo_location = GeoLocation.objects.create(
            address=restaurant.address,
            lat=restaurant_coords[1],
            long=restaurant_coords[0]
        )
        restaurant.geo_location = restaurant_geo_location
        restaurant.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_auto_20220801_1639'),
    ]

    operations = [
        migrations.RunPython(add_restaurants_coords)
    ]
