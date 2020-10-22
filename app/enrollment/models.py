from django.contrib.postgres.fields import JSONField
from django.db import models
import uuid
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UpdatedAt', auto_now=True)
    active_status = models.BooleanField(db_column='ActiveStatus', default=True)

    class Meta:
        abstract = True


class Product(BaseModel):
    id = models.UUIDField(db_column='ProductID', primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey('registration.Store', db_column='StoreID', on_delete=models.CASCADE, related_name='products')
    course_id = models.CharField(db_column='CourseID', max_length=256)
    section_id = models.CharField(db_column='SectionID', max_length=256)
    course_title = models.CharField(db_column='CourseTitle', max_length=256)
    section_title = models.CharField(db_column='SectionTitle', max_length=256)
    delivery_method = models.CharField(db_column='DeliveryMethod', max_length=256)
    total_quantity = models.PositiveSmallIntegerField(db_column='TotalQuantity')
    sale_quantity = models.PositiveSmallIntegerField(db_column='SaleQuantity')
    reserved_quantity = models.PositiveSmallIntegerField(db_column='ReservedQuantity')
    available_quantity = models.PositiveSmallIntegerField(db_column='AvailableQuantity')
    is_expired = models.BooleanField(db_column='IsExpired', default=False)
    section_start_date = models.DateTimeField(db_column='SectionStartDate', null=True, blank=True)
    section_end_date = models.DateTimeField(db_column='SectionEndate', null=True, blank=True)
    course_slug = models.CharField(db_column='CourseSlug', max_length=256)

    def __str__(self):
        return f'{self.section_id}'


class Reservation(BaseModel):
    id = models.UUIDField(db_column='ReservationID', primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('enrollment.Product', db_column='ProductID', on_delete=models.CASCADE, related_name='reservations')
    creation_time = models.DateTimeField(db_column='CreationTime')
    expiration_time = models.DateTimeField(db_column='ExpirationTime')
    reservation_status = models.CharField(db_column='ReservationStatus', max_length=64)


class Cart(BaseModel):
    id = models.UUIDField(db_column='CartID', primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='carts')
    store = models.ForeignKey('registration.Store', db_column='StoreID', on_delete=models.CASCADE, related_name='carts')
    creation_time = models.DateTimeField(db_column='CreationTime', auto_now_add=True)
    last_update_time = models.DateTimeField(db_column='LastUpdateTime', auto_now=True)
    cart_status = models.CharField(db_column='CartStatus', max_length=16)
    cart_item_count = models.PositiveSmallIntegerField(db_column='CartItemCount')
    cart_item_total = models.FloatField(db_column='CartItemTotal')
    note = models.CharField(db_column='Note', max_length=16)


class CartItem(BaseModel):
    id = models.UUIDField(db_column='CartItemID', primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey('enrollment.Cart', db_column='CartID', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('enrollment.Product', db_column='ProductID', on_delete=models.CASCADE, related_name='cart_items')
    item_description = models.CharField(db_column='ItemDescription', max_length=64)
    creation_time = models.DateTimeField(db_column='CreationTime', auto_now_add=True)
    quantity = models.PositiveSmallIntegerField(db_column='Quantity')
    unit_price = models.PositiveSmallIntegerField(db_column='UnitPrice')
    item_total = models.FloatField(db_column='ItemTotal')
    item_status = models.CharField(db_column='ItemStatus', max_length=16)
    referral_code = models.CharField(db_column='ReferralCode', max_length=128)
    reservation = models.OneToOneField('enrollment.Reservation', db_column='ReservationID', on_delete=models.CASCADE, related_name='cart_item')


class Order(BaseModel):
    id = models.UUIDField(db_column='OrderID', primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey('registration.Store', db_column='StoreID', on_delete=models.CASCADE, related_name='orders')
    cart = models.OneToOneField('enrollment.Cart', db_column='CartID', on_delete=models.CASCADE, related_name='order')
    creation_time = models.DateTimeField(db_column='CreationTime', auto_now_add=True)
    last_update_time = models.DateTimeField(db_column='LastUpdateTime', auto_now=True)
    closed_time = models.DateTimeField(db_column='ClosedTime', null=True, blank=True)
    order_status = models.CharField(db_column='OrderStatus', max_length=16)
    is_canceled = models.BooleanField(db_column='IsCanceled', default=False)
    cancel_reason = models.CharField(db_column='CancelReason', null=True, blank=True, max_length=16)
    total_item_count = models.PositiveSmallIntegerField(db_column='TotalItemCount')
    total_amount = models.FloatField(db_column='TotalAmount')
    payment_status = models.CharField(db_column='PaymentStatus', max_length=16)
    note = models.CharField(db_column='Note', max_length=16)


class OrderStatusHistory(BaseModel):
    id = models.UUIDField(db_column='OrderStatusHistoryID', primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('enrollment.Order', db_column='OrderID', on_delete=models.CASCADE, related_name='order_status_histories')
    previous_status = models.CharField(db_column='PreviousStatus', max_length=16)
    present_status = models.CharField(db_column='PresentStatus', max_length=16)
    update_time = models.DateTimeField(db_column='UpdateTime')
    updated_by = models.CharField(db_column='UpdatedBy', max_length=64)
    note = models.CharField(db_column='Note', max_length=256)


class OrderItem(BaseModel):
    id = models.UUIDField(db_column='OrderItemID', primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('enrollment.Order', db_column='OrderID', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('enrollment.Product', db_column='ProductID', on_delete=models.CASCADE, related_name='order_items')
    item_description = models.CharField(db_column='ItemDescription', max_length=256)
    creation_time = models.DateTimeField(db_column='CreationTime')
    quantity = models.PositiveSmallIntegerField(db_column='Quantity')
    unit_price = models.FloatField(db_column='UnitPrice')
    item_total = models.FloatField(db_column='ItemTotal')
    referral_code = models.CharField(db_column='ReferralCode', max_length=256)
    reservation = models.OneToOneField('enrollment.Reservation', db_column='ReservationID', on_delete=models.CASCADE, related_name='order_item')


class PaymentGateway(BaseModel):
    id = models.UUIDField(db_column='PaymentGatewayID', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(db_column='Name', max_length=128)
    library_version = models.CharField(db_column='LibraryVersion', max_length=20, blank=True, null=True)
    last_update_date = models.DateField(db_column='LastUpdateDate', blank=True, null=True)
    is_active = models.BooleanField(db_column='isActive', default=False)
    library_path = models.FilePathField(db_column='LibraryPath', path=settings.PAYMENT_LIB_DIR, allow_files=False, allow_folders=True)
    class_name = models.CharField(db_column='ClassName', max_length=30, null=True, blank=True)


class Payment(BaseModel):
    id = models.UUIDField(db_column='PaymentID', primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('enrollment.Order', db_column='OrderID', on_delete=models.CASCADE, related_name='payments')
    payment_gateway = models.ForeignKey('enrollment.PaymentGateway', db_column='PaymentGatewayID', on_delete=models.CASCADE, related_name='payments')
    creation_time = models.DateTimeField(db_column='CreationTime', auto_now_add=True)
    last_update_time = models.DateTimeField(db_column='LastUpdateTime', auto_now_add=True)
    is_paid = models.BooleanField(db_column='IsPaid', default=False)
    payment_status = models.CharField(db_column='PaymentStatus', max_length=16)
    note = models.CharField(db_column='Note', max_length=256)


class PaymentTransaction(BaseModel):
    id = models.UUIDField(db_column='PaymentTransactionID', primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey('enrollment.Payment', db_column='PaymentID', on_delete=models.CASCADE, related_name='payment_transactions')
    transaction_type = models.CharField(db_column='TransactionType', max_length=16)
    transaction_code = models.CharField(db_column='TransactionCode', max_length=256, null=True, blank=True)
    transaction_time = models.DateTimeField(db_column='TransactionTime', auto_now_add=True)
    currency_code = models.CharField(db_column='CurrencyCode', max_length=256)
    amount = models.FloatField(db_column='Amount')
    status = models.CharField(db_column='Status', max_length=16)
    transaction_reference = models.CharField(db_column='TransactionReference', max_length=256, null=True, blank=True)
    transaction_detail = JSONField(db_column='TransactionDetail', null=True, blank=True)


class PaymentGatewayConfig(BaseModel):
    id = models.UUIDField(db_column='PaymentGatewayConfigID', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(db_column='Name', max_length=128)
    config = JSONField(db_column='Config')


class StorePaymentGateway(BaseModel):
    id = models.UUIDField(db_column='StorePaymentGatewayID', primary_key=True, default=uuid.uuid4, editable=False)
    payment_gateway = models.ForeignKey('enrollment.PaymentGateway', db_column='PaymentGatewayID', on_delete=models.CASCADE, related_name='store_payment_gateways')
    store = models.ForeignKey('registration.Store', db_column='StoreID', on_delete=models.CASCADE, related_name='store_payment_gateways')
    payment_gateway_config = models.ForeignKey('enrollment.PaymentGatewayConfig', db_column='PaymentGatewayConfig', on_delete=models.SET_NULL, null=True, related_name='store_payment_gateways')
    branding = JSONField(db_column='Branding')

    def __str__(self):
        return f'{self.payment_gateway.name} - {self.store.name}'


class Enrolment(BaseModel):
    id = models.UUIDField(db_column='PaymentGatewayID', primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='enrolments')
    name = models.CharField(db_column='Name', max_length=128)
    course_id = models.CharField(db_column='CourseID', max_length=256)
    section_id = models.CharField(db_column='SectionID', max_length=256)
    enrolment_time = models.DateTimeField(db_column='EnrolmentTime')
    application_time = models.DateTimeField(db_column='ApplicationTime')
    enrolment_status = models.CharField(db_column='EnrolmentStatus', max_length=16)


class EnrolmentStatusHistory(BaseModel):
    id = models.UUIDField(db_column='EnrolmentStatusID', primary_key=True, default=uuid.uuid4, editable=False)
    enrolment = models.ForeignKey('enrollment.Enrolment', db_column='EnrolmentID', on_delete=models.CASCADE, related_name='enrolment_status_histories')
    previous_status = models.CharField(db_column='PreviousStatus', max_length=16)
    present_status = models.CharField(db_column='PresentStatus', max_length=16)
    update_by = models.CharField(db_column='UpdateBy', max_length=256)
    update_time = models.DateTimeField(db_column='UpdateTime')
    application_time = models.DateTimeField(db_column='ApplicationTime')
    erp_request = JSONField(db_column='ERPRequest')
    erp_request_code = models.CharField(db_column='ERPResponseCode', max_length=16)
    erp_response = JSONField(db_column='ERPResponse')
