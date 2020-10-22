import os
import sys
import django
from python_graphql_client import GraphqlClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_identity.settings')
django.setup()

from enrollment.models import *
from registration.models import *
from decouple import config


def get_data():
    client = GraphqlClient(endpoint=config('CAMPUS_API_URL'))
    query = """
        query coursesQuery {
          courses {
            edges {
            node {
              id
              provider{
                id
                name
                code
              }
            code
            title
            slug
            sections {
              edges {
                node {
                  code
                  startDate
                  endDate
                  description
                  courseFee {
                    amount
                  }
                }
              }
            }
          }
      }
    }
        }
    """
    return client.execute(query=query)


def save_products():
    data = get_data()
    index = 0

    for item in data['data']['courses']['edges']:
        store, created = Store.objects.get_or_create(
            course_provider_code=item['node']['provider']['code'],
            name=item['node']['provider']['name'],
            url_slug=item['node']['provider']['code'],
            defaults={
                'course_provider_code': item['node']['provider']['code'],
                'name': item['node']['provider']['name'],
                'url_slug': item['node']['provider']['code']
            }
        )
        if created:
            print('Store created')
        else:
            print('Store Already Exists')
        for section in item['node']['sections']['edges']:
            product, created = Product.objects.get_or_create(
                store=store,
                section_id=section['node']['code'],
                defaults={
                    'store': store,
                    'section_id': section['node']['code'],
                    'course_id': item['node']['code'],
                    'course_title': item['node']['title'],
                    'section_title': section['node']['code'],
                    'delivery_method': 'Online',
                    'total_quantity': 20,
                    'sale_quantity': 0,
                    'reserved_quantity': 0,
                    'available_quantity': 20,
                    'is_expired': False,
                    'section_start_date': section['node']['startDate'],
                    'section_end_date': section['node']['endDate'],
                    'course_slug': item['node']['slug'],
                }
            )
            if created:
                index += 1
                print('Product created:-' + str(index))
            else:
                print('Product Already Exists')


if __name__ == '__main__':
    # Store.objects.all().delete()
    # Product.objects.all().delete()
    save_products()
