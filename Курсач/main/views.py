import random
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import RegisterForm, NewProduct
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from datetime import datetime
from django.utils import timezone
from django.template.defaulttags import register
@register.filter
def get_key(dictionary, key):
    return dictionary[key]
@register.filter
def arr(array, index):
    return array[index]

# Представление для главной страницы
def index(request):
    products = Product.objects.all()
    if request.method == "POST":
        messages.success(request, f"{products.name} добавлен в вашу корзину.")
        return redirect("main:add_to_cart", product_name=products.name)
    return render(request, 'main/index.html', {'products': products})

# Представление для профиля пользователя
@login_required
def profile_view(request):
    user = request.user
    if user.registration_code_flag == 0:
        a = 0
        user.registration_code = a

    if request.method == 'POST':
        a = random.randint(1, 1000000)
        flag = True
        user.registration_code = a


        user.registration_code_flag = flag
        user.save()
    return render(request, 'main/profile.html')

# Представление для регистрации пользователя
class register_view(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy("main:profile")
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# Представление для добавления товаров в корзину
@login_required
def add_to_cart(request, product_name):
    cart_item = Cart.objects.filter(user=request.user, product=product_name).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Товар добавлен в вашу корзину.")
    else:
        Cart.objects.create(user=request.user, product=product_name)
        messages.success(request, "Товар добавлен в вашу корзину.")

    return redirect("main:cart_detail")

# Представление для удаления товаров из корзины
@login_required
def remove_from_cart(request, product_name):
    cart_item = get_object_or_404(Cart, product=product_name)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, "Товар удален из вашей корзины.")

    return redirect("main:cart_detail")

# Представление для отображения деталей корзины
@login_required
def cart_detail(request):
    context = {
        "cart_items": '',
        "total_price": '',
        'error': 0,
    }
    cart_items = Cart.objects.filter(user=request.user)

    for item in cart_items:
        item.price = Product.objects.get(name=item.product).price
        item.QP = item.quantity * item.price
        item.save()
    total_price = sum(item.quantity * item.price for item in cart_items)


    if 'Buy' in request.POST:
        if request.POST['Buy'] == 'Купить':
            user = request.user
            payment_method = request.POST['payment']
            cart_items = Cart.objects.filter(user=user)
            my_user = get_object_or_404(User, pk=user.id)

            if cart_items:
                if payment_method == 'card':
                    if  total_price <= my_user.balance:
                        my_user.total_purchase += total_price
                        my_user.balance -= total_price

                        for item in cart_items:
                            order = Order()
                            order.user = user
                            order.product = item.product
                            order.quantity = item.quantity
                            order.price = item.price
                            order.date_time = datetime.now()
                            order.payment_method = payment_method
                            order.save()

                        for item in cart_items:
                            prdct = get_object_or_404(Product, name=item.product)
                            prdct.amount -= item.quantity
                        else:
                            prdct.save()

                        Cart.objects.filter(user=user).delete()
                        my_user.save()


                        return redirect('main:cart_detail')
                    else:
                        context['error'] = 1

                elif payment_method == 'cash':
                    my_user.total_purchase += total_price

                    for item in cart_items:
                        order = Order()
                        order.user = user
                        order.product = item.product
                        order.quantity = item.quantity
                        order.price = item.price
                        order.date_time = datetime.now()
                        order.payment_method = payment_method
                        order.save()

                    for item in cart_items:
                        prdct = get_object_or_404(Product, name=item.product)
                        prdct.amount -= item.quantity
                    else:
                        prdct.save()

                    Cart.objects.filter(user=user).delete()
                    my_user.save()

                    return redirect('main:cart_detail')



    context['cart_items'] = cart_items
    context['total_price'] = total_price


    return render(request, "cart/cart_detail.html", context)



@login_required()
def orders_detail(request):
    context = {
        'order_items': '',
        'error': 0,
    }

    user = request.user
    orders = Order.objects.filter(user_id=user.id).order_by('date_time')
    context['order_items'] = orders

    if request.POST:
        product_id = request.POST['return']
        quantity = int(request.POST['quantity'])
        reason = request.POST['reason']
        product = orders.get(product=product_id)
        my_user = User.objects.get(id=user.id)

        if quantity < product.quantity:
            my_return = Returns()
            my_return.product = product_id
            my_return.price = product.price
            my_return.quantity = quantity
            my_return.user = user
            my_return.payment_method = product.payment_method
            my_return.reason = reason
            my_return.date_time = timezone.now()

            if my_return.payment_method == 'card':
                my_user.balance += my_return.total_price()
                my_user.save()

            my_return.save()





            product.quantity -= quantity
            product.save()

        elif quantity == product.quantity:

            my_return = Returns.objects.create(user=user, product=product_id, quantity=quantity, price=product.price, payment_method=product.payment_method, reason=reason, date_time=timezone.now())

            if my_return.payment_method == 'card':
                my_user.balance += my_return.total_price()
                my_user.save()

            my_return.save()


            product.delete()

        else:
            context['error'] = 1



    return render(request, "orders/orders_detail.html", context)


# Представление для добавления нового товара
def add_new_item(request):
    if request.method == "POST":
        form = NewProduct(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            form = NewProduct()

    products = Product.objects.all()
    return render(request, 'main/index.html', {'products': products})


@permission_required(perm='main.otchet', raise_exception=True)
def otchet(request):
    context = {}

    orders = Order.objects.all()
    returns = Returns.objects.all()
    data = {
        'card': {},
        'cash': {},
        'return': {}
    }

    for order in orders:
        date = order.date_time.date().strftime("%d.%m.%Y")
        if date in data[order.payment_method]:
            data[order.payment_method][date].append([order.product, order.total_price()])
        else:
            data[order.payment_method][date]  = [[order.product, order.total_price()]]
    for r in returns:
        date = r.date_time.date().strftime("%d.%m.%Y")
        if date in data['return']:
            data['return'][date].append([r.product, r.total_price()])
        else:
            data['return'][date]  = [[r.product, r.total_price()]]

    card_sum = 0
    for i in data['card']:
        for j in data['card'][i]:
            card_sum += float(j[1])
    cash_sum = 0
    for i in data['cash']:
        for j in data['cash'][i]:
            cash_sum += float(j[1])
    return_sum = 0
    for i in data['return']:
        for j in data['return'][i]:
            return_sum += float(j[1])
    print(data)
    prices = {
        'card': [card_sum, {}],
        'cash': [cash_sum, {}],
        'return': [return_sum, {}]
    }

    for order in orders:
        date = order.date_time.date().strftime("%d.%m.%Y")
        summ = 0
        for d in data[order.payment_method][date]:
            summ += float(d[1])
        prices[order.payment_method][1][date] = summ

    # for order in orders:
    #     date = order.date_time.date().strftime("%d.%m.%Y")
    #     summ = 0
    #     for d in data['cash'][date]:
    #         summ += float(d[1])
    #     prices['cash'][1][date] = summ

    for r in returns:
        date = r.date_time.date().strftime("%d.%m.%Y")
        summ = 0
        for d in data['return'][date]:
            summ += float(d[1])
        prices['return'][1][date] = summ

    print(prices)


    sum_by_day = {}

    for order in orders:
        date = order.date_time.date().strftime("%d.%m.%Y")
        if date in sum_by_day:
            sum_by_day[date] += prices[order.payment_method][1][date]
        else:
            sum_by_day[date] = prices[order.payment_method][1][date]

    context['sum_by_day'] = sum_by_day
    context['data'] = data
    context['prices'] = prices

    return render(request, 'main/otchet.html', context=context)