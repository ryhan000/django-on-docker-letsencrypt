from enrollment_api.shared_function import SharedMixin, CourseMixin
from enrollment_api.serializers import *

from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import viewsets

from django.http import HttpResponse

from enrollment.models import *
from registration.models import *
from rest_framework.status import *

from shared_libs.auth_decorators import IsAuthenticated
from shared_libs.exceptions import *

import importlib.util
import os

import logging

logger = logging.getLogger('campus_identity_provider')


class SectionReservationViewSet(CourseMixin, SharedMixin, viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        profile = request.profile
        section_code = self.request.query_params.get('section_code', None)
        quantity = self.request.query_params.get('quantity', 1)
        provider = self.request.query_params.get('provider', None)
        course_slug = self.request.query_params.get('course', None)
        logger.info(f'Trying to reserved a section for {profile.first_name} {profile.last_name}!')
        product = self.get_product(section_code)
        data = self.get_course_from_markateplace_backend(provider, course_slug, None)
        course_fee_amount = self.get_course_ammount_fee(section_code, data)
        return Response(self.create_section_reservation(profile, product, course_fee_amount, quantity), status=HTTP_200_OK)


class RenewSectionReservationViewSet(SharedMixin, viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        profile = request.profile
        logger.info(f'Trying to renew a section reservation for {profile.first_name} {profile.last_name}!')
        reservation_id = self.request.query_params.get('reservation_code', None)
        quantity = self.request.query_params.get('quantity', 1)
        section_code = self.request.query_params.get('section_code', None)
        old_reservation = self.get_reservation(reservation_id)
        self.update_reservation(old_reservation, 'Canceled')
        product = self.get_product(section_code)
        course_fee_amount = self.get_reservation_fee_amount(old_reservation)
        return Response(self.create_section_reservation(profile, product, course_fee_amount, quantity), status=HTTP_200_OK)


class GetEnrollmentDetailsGatewayViewSet(CourseMixin, viewsets.ViewSet):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        provider = self.request.query_params.get('provider', None)
        course_slug = self.request.query_params.get('course', None)
        course_provider_code = self.request.query_params.get('store', None)
        logger.info(f'Trying to get enrollment details and payment gateways!')
        if course_slug and provider:
            payment_gateway_ids = [item.payment_gateway.id for item in StorePaymentGateway.objects.filter(store__course_provider_code=provider)]
            payment_gateways = PaymentGateway.objects.filter(id__in=payment_gateway_ids)
            return Response(self.get_course_from_markateplace_backend(provider, course_slug, payment_gateways), status=HTTP_200_OK)
        logger.info(f'Enrollment details and payment gateways not found!')
        raise ContentNotFoundException()


class GetCourseDetailsGatewayViewSet(CourseMixin, viewsets.ViewSet):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        provider = self.request.query_params.get('provider', None)
        course_slug = self.request.query_params.get('course', None)
        logger.info(f'Trying to get course details and payment gateways!')
        if course_slug and provider:
            return Response(self.get_course_from_markateplace_backend(provider, course_slug, None), status=HTTP_200_OK)
        logger.info(f'Course details and payment gateways not found!')
        raise ContentNotFoundException()


class GetEnrollmentViewSet(SharedMixin, viewsets.ModelViewSet):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get enrolled course for {request.profile.first_name} {request.profile.last_name}!')
        queryset = Enrolment.objects.filter(profile=request.profile)
        serializer = EnrolmentSerializer(queryset, many=True, context={'request': request})
        data = {'data': serializer.data}
        logger.info(f'Got {queryset.count()} enrolled course!')
        return Response(data, status=HTTP_200_OK)


class PaymentInitiateViewSet(SharedMixin, viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        reservation_id = self.request.query_params.get('reservation_code', None)
        course_fee = self.request.query_params.get('course_fee', None)
        section_code = self.request.query_params.get('section_code', None)
        provider = self.request.query_params.get('provider', None)
        course_slug = self.request.query_params.get('course', None)

        logger.info(f'Trying to payment initiate for {request.profile.first_name} {request.profile.last_name}!')

        reservation = self.get_reservation(reservation_id)

        self.check_reservation(reservation)
        reserved_section_course_fee = self.get_reservation_fee_amount(reservation)

        if reserved_section_course_fee != int(course_fee):
            raise SectionCourseFeeNotMatchException()

        if not section_code and not provider and not course_slug:
            raise ParametersNotFoundException()

        store_payment_gateway = StorePaymentGateway.objects.filter(store=reservation.product.store).first()
        config = store_payment_gateway.payment_gateway_config
        file_path = os.path.join(store_payment_gateway.payment_gateway.library_path, '__init__.py')

        spec = importlib.util.spec_from_file_location(config.name, file_path)
        payment_provider = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(payment_provider)

        # this part is not generic yet
        processing_url = f'https://enrollment.dev.campus.com/{provider}/{course_slug}/{section_code}/PROCESSING/?order_id={reservation.order_item.order.id}'
        cancel_url = f'https://enrollment.dev.campus.com/{provider}/{course_slug}/{section_code}/CANCEL'

        payment_form_data, page_resp = payment_provider.get_an_accept_payment_page(
            processing_url,
            cancel_url,
            reserved_section_course_fee,
            config.config['login_id'],
            config.config['transaction_key']
        )

        data = {'data': payment_form_data}

        # this part will change
        product = reservation.product
        self.create_enrolment(product.course_title, request.profile, product.course_id, product.section_id)
        payment = self.create_payment(reservation.order_item.order, self.payment_gateway(), True, 'SUCCESS')
        self.create_payment_transaction(payment, reservation.order_item.order, 'SUCCESS')
        self.update_reservation(reservation, 'Reserved')

        return Response(data, status=HTTP_200_OK)


class CheckPaymentStatusViewSet(SharedMixin, viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        order_id = self.request.query_params.get('order_id', None)
        order = self.get_order(order_id)
        # this part will change
        order.payment_status = 'SUCCESS'
        order.save()
        data = {'data': {'payment_status': order.payment_status}}
        print(data)
        return Response(data, status=HTTP_200_OK)


def webhooks(request):
    for key, value in request.POST.items():
        print('Key: %s' % (key))
        print('Value %s' % (value))
    for key, value in request.GET.items():
        print(key, value)
