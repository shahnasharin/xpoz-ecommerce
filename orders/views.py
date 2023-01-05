from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
import datetime
from .models import Order,OrderProduct, Payment
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
# Create your views here.

# def place_order(request,total=0, quantity=0):
#     # return HttpResponse('ok')
#     current_user = request.user

# from django.shortcuts import render, redirect
# from django.http import HttpResponse, JsonResponse
# from carts.models import CartItem
# from .forms import OrderForm
# import datetime
# from .models import Order, Payment, OrderProduct
# import json
# from store.models import Product
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string


def payments(request):
    return render(request,'orders/payments.html')
#     body = json.loads(request.body)
#     order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    # payment = Payment(
    #     user = request.user,
    #     payment_id = body['transID'],
    #     payment_method = body['payment_method'],
    #     amount_paid = order.order_total,
    #     status = body['status'],
    # )
    # payment.save()

    # order.payment = payment
    # order.is_ordered = True
    # order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    cart_count = cart_items.count()
    if cart_count<=0:
        return redirect('store')

    
#     for item in cart_items:
#         orderproduct = OrderProduct()
#         orderproduct.order_id = order.id
#         orderproduct.payment = payment
#         orderproduct.user_id = request.user.id
#         orderproduct.product_id = item.product_id
#         orderproduct.quantity = item.quantity
#         orderproduct.product_price = item.product.price
#         orderproduct.ordered = True
#         orderproduct.save()

#         cart_item = CartItem.objects.get(id=item.id)
#         product_variation = cart_item.variations.all()
#         orderproduct = OrderProduct.objects.get(id=orderproduct.id)
#         orderproduct.variations.set(product_variation)
#         orderproduct.save()


#         # Reduce the quantity of the sold products
#         product = Product.objects.get(id=item.product_id)
#         product.stock -= item.quantity
#         product.save()

#     # Clear cart
#     CartItem.objects.filter(user=request.user).delete()

#     # Send order recieved email to customer
#     mail_subject = 'Thank you for your order!'
#     message = render_to_string('orders/order_recieved_email.html', {
#         'user': request.user,
#         'order': order,
#     })
#     to_email = request.user.email
#     send_email = EmailMessage(mail_subject, message, to=[to_email])
#     send_email.send()

#     # Send order number and transaction id back to sendData method via JsonResponse
#     data = {
#         'order_number': order.order_number,
#         'transID': payment.payment_id,
#     }
#     return JsonResponse(data)
@login_required(login_url='signin')
def razorpay_check(request):
    print('this arazorpay check ')
    if request.method == "POST":
        print('=-================asdfafafa====================dfafadfa=f=======================')
        payment_order = Payment()
        payment_order.user = request.user
        payment_order.payment_method = request.POST.get('payment_mode')
        if request.POST.get('payment_id'):
            payment_order.payment_id = request.POST.get('payment_id')
        payment_order.amount_paid = request.POST.get('grand_total')
        payment_order.status = True
        payment_order.save()
        print("payment is saved")

        order_number = request.POST.get('order_no')
        order = Order.objects.get(user=request.user, order_number=order_number)
        order.payment = payment_order
        order.is_ordered = True
        order.status = 'Processing'
        print('order status updated============================')
        print("Grand total", request.POST.get('grand_total'))
        order.order_total = request.POST.get('grand_total')
        print(order.order_total)

        print('order total are updated ============================')
        order.save()

        # moving the order details into order product table

        cart_items = CartItem.objects.filter(user=request.user)
        for cart_item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment_order
            order_product.user = request.user
            order_product.product = cart_item.product
            order_product.quantity = cart_item.quantity
            order_product.product_price = cart_item.product.price
            order_product.ordered = True
            order_product.save()

            item = CartItem.objects.get(id=cart_item.id)
            product_variation = item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()

            # reducing the quantity of product after selling it
            product = Product.objects.get(id=cart_item.product_id)
            product.stock -= cart_item.quantity
            product.save()

        # deleting the cart itemszzzzzzzzzzzzzzz
        CartItem.objects.filter(user=request.user).delete()

        # send order number and transaction id

        data = {
            'order_number': order_number,
            'tansID': payment_order.payment_id,
        }
        print("completed")
        # return render(request,'orders/order_completed.html')
        return JsonResponse({'status': 'Your order placed successfully!','data':data})



def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    # if cart_count <= 0:
    #     return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
           
    else:
        return redirect('checkout')


@login_required(login_url='login')
def order_completed(request):
    order_number = request.GET.get('order_number')
    print(order_number)

    try:
        order = Order.objects.get(order_number=order_number)
        order.status = 'Accepted'
        order.save()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0

        for item in ordered_products:
            subtotal += (item.product_price * item.quantity)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'sub_total': subtotal
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')