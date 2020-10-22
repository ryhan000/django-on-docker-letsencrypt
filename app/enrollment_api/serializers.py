from rest_framework import serializers
from enrollment.models import *
from registration.models import *


class PaymentGatewaySerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentGateway
        fields = ('id', 'name')

class EnrolmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enrolment
        fields = ('id', 'profile', 'name', 'course_id', 'section_id', 'enrolment_time', 'application_time', 'enrolment_status')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        product = Product.objects.filter(course_id=data['course_id'], section_id=data['section_id'])

        if product.exists():
            item = product.filter().first()
            data['course_title'] = item.course_title
            data['section_start_date'] = item.section_start_date
            data['section_end_date'] = item.section_end_date
            data['course_slug'] = item.course_slug
            data['course_provider'] = item.store.course_provider_code

        return data
