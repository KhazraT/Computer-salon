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


                # for item in cart_items:
                #     order = Order()
                #     order.user = user
                #     order.product = item.product
                #     order.quantity = item.quantity
                #     order.price = Product.objects.get(name=item.product).price
                #     order.date_time = datetime.now()
                #     order.save()
                #     remove_from_cart(request, item.product)


    context['cart_items'] = cart_items
    context['total_price'] = total_price


    return render(request, "cart/cart_detail.html", context)

# Представление для обработки заказов
# @login_required
# def orders(request):
#     user = request.user
#     cart_items = Cart.objects.filter(user=request.user)
#     for item in cart_items:
#         order = Order()
#         order.user = user
#         order.product = item.product
#         order.quantity = item.quantity
#         order.price = Product.objects.get(name=item.product).price
#         order.date_time = datetime.now()
#         order.save()
#         remove_from_cart(request, item.product)
#     user.balance -= sum(item.quantity * Product.objects.get(name=item.product).price for item in cart_items)
#     user.save()
#     return render(request, "cart/cart_detail.html")


def orders_detail(request):
    context = {
        ''
    }

    user = request.user
    orders = Order.objects.filter(user_id=user.id)
    for order in orders:
        print(order)
#номер заказа

    return render(request, "orders/orders_detail.html", context)

    # return HttpResponse("<h1>Доработать надо</h1>")

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
