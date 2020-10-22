from python_graphql_client import GraphqlClient

from shared_libs.exceptions import *

from registration.models import *

from enrollment_api.serializers import *
from enrollment.models import *

from decouple import config

from datetime import datetime, timedelta
import pytz

class SharedMixin(object):

    # product
    def get_product(self, section_id):
        try:
            product = Product.objects.get(section_id=section_id)
        except Product.DoesNotExist:
            logger.info(f'Section not found!')
            raise SectionNotFoundException()

        if product.is_expired:
            logger.info(f'Section has expired!')
            raise ExpiredSectionException()
        elif product.available_quantity <= 0:
            logger.info(f'Section seat not available!')
            raise SectionSeatNotAvailableException()
        elif product.total_quantity <= 0:
            logger.info(f'Section seat not available!')
            raise SectionSeatNotAvailableException()

        return product

    def update_product(self, reservation, quantity):
        product = Product.objects.get(id=reservation.product.id)
        product.available_quantity -= quantity
        product.sale_quantity += quantity
        product.save()

    # reservation
    def get_reservation(self, id):
        try:
            reservation = Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            logger.info(f'Reservation not found!')
            raise ReservationNotFoundException()
        return reservation

    def check_reservation(self, reservation):
        if reservation.expiration_time.replace(tzinfo=pytz.utc) < datetime.now().replace(tzinfo=pytz.utc):
            logger.info(f'Reservation has expired!')
            raise ExpiredReservationException()

    def create_reservation(self, product):
        return Reservation.objects.create(
            product=product,
            creation_time=datetime.now().replace(tzinfo=pytz.utc),
            expiration_time=datetime.now().replace(tzinfo=pytz.utc) + timedelta(minutes=2),
            reservation_status='Start',
        )

    def update_reservation(self, reservation, reservation_status):
        reservation = Reservation.objects.get(id=reservation.id)
        reservation.reservation_status = reservation_status
        reservation.save()

    def get_reservation_fee_amount(self, reservation):
        return reservation.order_item.order.total_amount

    # cart
    def create_cart(self, profile, product):
        return Cart.objects.create(
            profile=profile,
            store=product.store,
            cart_status='Create',
            cart_item_count=0,
            cart_item_total=0,
            note='Note',
        )

    def update_cart(self, cart, cart_item):
        cart = Cart.objects.get(id=cart.id)
        cart.cart_item_count += cart_item.quantity
        cart.cart_item_total += (cart_item.quantity * cart_item.unit_price)
        cart.save()

    def create_cart_item(self, price, product, quantity, cart, reservation):
        cart_item = CartItem.objects.filter(reservation=reservation)
        if not cart_item.exists():
            return CartItem.objects.create(
                cart=cart,
                product=product,
                item_description='Item Description',
                creation_time=datetime.now(),
                quantity=quantity if quantity else 1,
                unit_price=price,
                item_total=(price * quantity) if quantity else (price * 1),
                item_status='Item status',
                referral_code='Referral code',
                reservation=reservation,
            )
        return cart_item.filter().first()

    def get_cart_item(self, reservation):
        return CartItem.objects.filter(reservation=reservation)

    # order
    def create_order(self, cart_item):
        order = Order.objects.filter(cart=cart_item.cart)
        if not order.exists():
            return Order.objects.create(
                profile=cart_item.cart.profile,
                store=cart_item.cart.store,
                cart=cart_item.cart,
                order_status='Create',
                total_item_count=cart_item.cart.cart_item_count,
                total_amount=cart_item.cart.cart_item_total,
                payment_status='PROCESSING',
                note='Note',
            )

        return order

    def get_order(self, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            logger.info(f'Order not found!')
            raise OrderNotFoundException()
        return order

    def create_order_item(self, cart_item):
        order = self.create_order(cart_item.filter().first())
        for item in cart_item:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                item_description=item.item_description,
                creation_time=item.creation_time,
                quantity=item.quantity,
                unit_price=item.unit_price,
                item_total=item.item_total,
                referral_code=item.referral_code,
                reservation=item.reservation
            )
        return order

    # payment gateway
    def get_payment_gateway(self, payment_gateway_id):
        try:
            payment_gateway = PaymentGateway.objects.get(id=payment_gateway_id)
        except PaymentGateway.DoesNotExist:
            logger.info(f'Payment Gateway not found!')
            raise PaymentGatewayNotFoundException()
        return payment_gateway

    def payment_gateway(self):
        return PaymentGateway.objects.all().first()

    def create_payment_transaction(self, payment, order, status):
        return PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='PURCHASE',      
            currency_code='USD',
            amount=order.total_amount,
            status=status,
        )

    def create_payment(self, order, payment_gateway, is_paid, payment_status):
        return Payment.objects.create(
            order=order,
            payment_gateway=payment_gateway,
            is_paid=is_paid,
            payment_status=payment_status,
            note="Note",
        )

    def get_course_ammount_fee(self, section_code, data):
        try:
            for section in data['data']['course']['sections']['edges']:
                if section_code == section['node']['code']:
                    return section['node']['courseFee']['amount']
        except:
            logger.info(f'Provide a valid provider and course name!')
            raise CourseFeeNotFoundException()

    def create_section_reservation(self, profile, product, course_fee_amount, quantity):
        reservation = self.create_reservation(product)
        cart = self.create_cart(profile, product)
        cart_item = self.create_cart_item(int(course_fee_amount), product, int(quantity), cart, reservation)
        self.update_cart(cart, cart_item)
        cart_item = self.get_cart_item(reservation)
        self.create_order_item(cart_item)

        data = {
            'data': {
                'reservation_code': reservation.id,
                'expiration_time': reservation.expiration_time,
                'creation_time': reservation.creation_time
            }
        }
        logger.info(f'Succesfully reserved a section for {profile.first_name} {profile.last_name}!')
        return data

    # Enrolment
    def create_enrolment(self, course_title, profile, course_id, section_id):
        return Enrolment.objects.create(
            profile=profile,
            name=course_title,
            course_id=course_id,
            section_id=section_id,
            enrolment_time=datetime.now().replace(tzinfo=pytz.utc),
            application_time=datetime.now().replace(tzinfo=pytz.utc),
            enrolment_status='ENROLLED',
        )

class CourseMixin(object):

    def get_course_from_markateplace_backend(self, provider, course_slug, payment_gateways):
        client = GraphqlClient(endpoint=config('CAMPUS_API_URL'))
        query = """
            query courseQuery($providerCode: String, $slug: String){
              course(providerCode: $providerCode, slug: $slug) {
                code
                title
                slug
                provider {
                  code
                }
                sections {
                  edges {
                    node {
                      id
                      code
                      startDate
                      endDate
                      courseFee {
                        amount
                      }
                      executionMode
                      executionSite {
                        code
                      }
                    }
                  }
                }
              }
            }
        """
        variables = {"providerCode": provider, "slug": course_slug}
        data = client.execute(query=query, variables=variables)
        if payment_gateways:
            data['data']['payment_gateways'] = PaymentGatewaySerializer(payment_gateways, many=True).data
        logger.info(f'Succesfully got data from markateplace backend!')
        return data
