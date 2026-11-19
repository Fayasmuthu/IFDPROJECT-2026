from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Payment, Coupon, WhatsAppOrder, Wishlist, Notification


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'full_name',
        'email',
        'mobile_no',
        'payable',
        'payment_method',
        'payment_status',
        'order_status',
        'created',
        'is_ordered',
    )
    list_display_links = ('order_id', 'full_name')
    list_filter = (
        'order_status',
        'payment_status',
        'payment_method',
        'is_ordered',
        'created',
        'state',
    )
    search_fields = (
        'order_id',
        'full_name',
        'email',
        'mobile_no',
        'razorpay_payment_id',
        'city',
        'state',
    )
    ordering = ('-created', '-id')
    date_hierarchy = 'created'
    list_per_page = 25
    list_editable = ('order_status', 'payment_status')
    readonly_fields = ('order_id', 'unique_transaction_id', 'created', 'updated')
    inlines = [OrderItemInline, PaymentInline]

    fieldsets = (
        (_('Order Summary'), {
            'fields': (
                'order_id',
                'unique_transaction_id',
                'is_ordered',
                'created',
                'updated',
                'completed_at',
            )
        }),
        (_('Customer Details & Shipping'), {
            'fields': (
                'full_name',
                'email',
                'mobile_no',
                'alternative_no',
                'address_line_1',
                'address_line_2',
                'city',
                'district',
                'state',
                'pin_code',
            )
        }),
        (_('Payment & Amounts'), {
            'fields': (
                'payable',
                'subtotal',
                'service_fee',
                'shipping_fee',
                'payment_method',
                'payment_status',
                'razorpay_payment_id',
                'razorpay_order_id',
                'razorpay_signature',
            )
        }),
        (_('Status & Fulfillment'), {
            'fields': (
                'order_status',
            )
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'payment_method',
        'payment_id',
        'amount',
        'status',
        'timestamp',
    )
    list_filter = ('status', 'payment_method', 'timestamp')
    search_fields = (
        'payment_id',
        'order__order_id',
        'order__full_name',
        'order__email',
    )
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount',
        'active',
        'active_date',
        'expiry_date',
        'created_date',
    )
    list_filter = ('active', 'active_date', 'expiry_date')
    search_fields = ('code',)
    list_editable = ('active',)


@admin.register(WhatsAppOrder)
class WhatsAppOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'customer_phone',
        'product',
        'quantity',
        'selected_size',
        'status',
        'order_date',
    )
    list_filter = ('status', 'order_date')
    search_fields = ('customer_name', 'customer_phone', 'product__title')
    list_editable = ('status',)
    date_hierarchy = 'order_date'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    search_fields = ('user__username', 'user__email', 'product__product__title')
    raw_id_fields = ('user', 'product')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'description')
    search_fields = ('user__username', 'user__email', 'title', 'description')
    raw_id_fields = ('user',)
