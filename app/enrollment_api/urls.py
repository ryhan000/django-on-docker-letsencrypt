from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from enrollment_api.views import *

router = routers.DefaultRouter()
schema_view = get_swagger_view(title='Campus Identity API')

router.register(r'section_reservation', SectionReservationViewSet, 'section_reservation')
router.register(r'renew_section_reservation', RenewSectionReservationViewSet, 'renew_section_reservation')
router.register(r'get_enrollment_details', GetEnrollmentDetailsGatewayViewSet, 'get_enrollment_details')
router.register(r'get_course_details', GetCourseDetailsGatewayViewSet, 'get_course_details')
router.register(r'payment_initiate', PaymentInitiateViewSet, 'payment_initiate')
router.register(r'check_payment_status', CheckPaymentStatusViewSet, 'check_payment_status')
router.register(r'get_enrollments', GetEnrollmentViewSet, 'get_enrollments')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/', webhooks),
]
