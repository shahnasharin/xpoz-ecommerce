from django.urls import path
from . import views


urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order-completed/', views.order_completed, name="order_completed"),
    path('proceed-to-pay/', views.razorpay_check, name='razorpay_check'),

]