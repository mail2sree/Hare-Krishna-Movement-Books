from django.http import response
from razorpay.resources import order
from orders.models import Order, OrderProduct
from carts.models import Cart, CartItem
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .forms import OrderForm
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

import datetime
import razorpay

# Create your views here.

def payments(request):
    return render(request, 'orders/payments.html')

@csrf_exempt
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    shipping_charge = 50
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    shipping_charge = 0
    grand_total = total

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            formdata = Order()
            formdata.user = current_user
            formdata.first_name = form.cleaned_data['first_name']
            formdata.last_name = form.cleaned_data['last_name']
            formdata.phone = form.cleaned_data['phone']
            formdata.email = form.cleaned_data['email']
            formdata.address_line_1 = form.cleaned_data['address_line_1']
            formdata.address_line_2 = form.cleaned_data['address_line_2']
            formdata.country = form.cleaned_data['country']
            formdata.city = form.cleaned_data['city']
            formdata.state = form.cleaned_data['state']
            formdata.order_note = form.cleaned_data['order_note']
            formdata.order_total = grand_total
            formdata.shipping_charges = shipping_charge
            formdata.delivery_home = request.POST.get('HD')
            formdata.delivery_temple = request.POST.get('TP')
            formdata.ip = request.META.get('REMOTE_ADDR')
            formdata.save()
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(formdata.id)
            formdata.order_number = order_number
            formdata.save()
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
            client = razorpay.Client(auth=('rzp_live_8lfsEaPndygtIc', 'lFYQsGI3Spa3FTB69Gds1qlJ'))
            response_payment = client.order.create(dict(amount = grand_total * 100, 
                                                        currency="INR"))
            order_id = response_payment['id']
            order_status = response_payment['status']
            if order_status == 'created':
                formdata.order_id = order_id
                formdata.save()
                return render(request, 'orders/payments.html', {'order': order, 'cart_items': cart_items, 'total': total, 'gtotal': grand_total, 'shipping': shipping_charge, 'stotal': grand_total * 100, 'payment': response_payment})    

            return render(request, 'orders/payments.html', {'order': order, 'cart_items': cart_items, 'total': total, 'gtotal': grand_total, 'shipping': shipping_charge, 'stotal': grand_total * 100})
        else:
            return redirect('checkout')


def invoice(request):
    order = Order.objects.filter(user=request.user)
    if request.method == 'POST':
        response = request.POST
        parms_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }
        client = razorpay.Client(auth=('rzp_live_8lfsEaPndygtIc', 'lFYQsGI3Spa3FTB69Gds1qlJ'))
    
        try:
            status = client.utility.verify_payment_signature(parms_dict)
            order_status_1 = Order.objects.get(order_id=response['razorpay_order_id'])
            order_status_1.razorpay_order_id = response['razorpay_payment_id']
            order_status_1.is_ordered = True
            order_status_1.save()
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order_status_1.id
                order_product.payment = order_status_1.order_total
                order_product.user_id = request.user.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.save()
                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                order_product = OrderProduct.objects.get(id=order_product.id)
                order_product.variations.set(product_variation)
                order_product.save()
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()
            CartItem.objects.filter(user=request.user).delete()
            email_subject = 'You have recived a order'
            message1 = render_to_string('accounts/admin_order_info.html', {
		'user': request.user
	    })
            to_email = 'hkmhyderabadbooks@gmail.com'
            send_email = EmailMessage(email_subject, message1, to=[to_email])
            send_email.send()

            email_subject = 'Thank you for placing your order!'
            message = render_to_string('accounts/order_recived.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(email_subject, message, to=[to_email])
            send_email.send()
            return redirect('/orders/order_complete/?order_number='+str(order_status_1.order_number)+'&payment_id='+str(order_status_1.razorpay_order_id))
        except Exception as e:
            raise e

def order_complete(request):
    order_number = request.GET.get('order_number')
    razorpay_payment_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        return render(request, 'orders/order_complete.html', {'order': order, 'ordered_products': ordered_products, 'transID': razorpay_payment_id})
    except Exception as e:
        raise e
