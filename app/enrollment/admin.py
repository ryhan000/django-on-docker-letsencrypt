from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Reservation)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderStatusHistory)
admin.site.register(OrderItem)
admin.site.register(PaymentGateway)
admin.site.register(Payment)
admin.site.register(StorePaymentGateway)
admin.site.register(Enrolment)
admin.site.register(EnrolmentStatusHistory)
admin.site.register(PaymentGatewayConfig)
