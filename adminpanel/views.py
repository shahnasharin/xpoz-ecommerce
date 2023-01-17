from django.shortcuts import redirect,render
from django.contrib.auth.decorators import user_passes_test,login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from orders.models import *
from store.models import *
from accounts.models import Account
from category.models import category
from store.models import Variation
from .forms import ProductForm, VariationForm

def admin_dashboard(request):

    user_count = Account.objects.filter(is_superadmin=False).count()
    category_count = category.objects.filter().count()
    product_count = Product.objects.filter().count()
    variation_count = Variation.objects.all().count()
    order_count = OrderProduct.objects.filter(ordered=True).count()
    admin_order_count = Order.objects.filter(user__is_superadmin=True).count()

    # all_products = Product.objects.all()
    # print(all_products)
        
    
    context = {
        'user_count': user_count,
        'category_count': category_count,
        'product_count': product_count,
        'variation_count': variation_count,
        'order_count': order_count,
        'admin_order_count': admin_order_count,

        # 'all_products':all_products,
    }
    return render(request,'admin_panel/admin_dashboard.html',context)


#ADMIN USER MANAGEMENT

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def user_management(request):
    if 'key' in request.GET:
        key = request.GET['key']
        print(key)
        users = Account.objects.order_by('-id').filter(Q(first_name__icontains=key) | Q(email__icontains=key))
        print('if function')
    else:
        users = Account.objects.filter(is_superadmin=False).order_by('id')
        print(users)

    paginator = Paginator(users, 4)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)

    context = {
        'users': paged_users,
    }
    return render(request, 'admin_panel/user_management.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def user_ban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('user_management')



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def user_unban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_management')



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def product_management(request):
    if request.method == 'POST':
        key = request.POST['key']
        products = Product.objects.filter(Q(product_name__startswith=key) | Q(
            slug__startswith=key) | Q(category__category_name__startswith=key)).order_by('id')
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 4)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)

    context = {
        'products': paged_product,
    }
    return render(request, 'admin_panel/product_management.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm()
        context = {
            'form': form
        }
        return render(request, 'admin_panel/add_product.html', context)



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        try:
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
               
                return redirect('product_management')
            

        except Exception as e:
            raise e

    context = {
        'product': product,
        'form': form
    }
    return render(request, 'admin_panel/edit_product.html', context)

@login_required(login_url='signin')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('product_management')


#ORDER MANAGEMENT
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def order_management(request):
    if request.method == 'POST':
        key = request.POST['key']
        orders = Order.objects.filter(Q(is_ordered=True), Q(order_number__contains=key) | Q(user__email__contains=key) | Q(first_name__icontains=key)).order_by('id')
    else:
        orders = Order.objects.filter(is_ordered=True).order_by('id')

    paginator = Paginator(orders, 4)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    context = {
        'orders': paged_orders
    }
    return render(request, 'admin_panel/order_management.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def accept_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Shipped'
    order.save()

    return redirect('order_management')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def complete_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Delivered'
    order.save()

    return redirect('order_management')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def manager_cancel_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Cancelled'
    order.save()

    return redirect('order_management')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def cancel_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Cancelled'
    order.save()

    return redirect('admin_orders')


# ADMIN CATEGORY MANAGEMENT
@login_required(login_url='signin')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def category_management(request):
    if request.method == 'POST':
        key = request.POST['keyword']
        categories = category.objects.filter(Q(category_name__startswith=key) | Q(slug__startswith=key)).order_by('id')
    else:
        categories = category.objects.all().order_by('id')

    paginator = Paginator(categories, 4)
    page = request.GET.get('page')
    paged_categories = paginator.get_page(page)

    context = {
        'categories': paged_categories
    }
    return render(request, 'admin_panel/category_management.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def add_category(request):
    if request.method == 'POST':
        try:
            category_name = request.POST['category_name']
            category_slug = request.POST['category_slug']
            category_description = request.POST['category_description']

            categories = category(
                category_name=category_name,
                slug=category_slug,
                desciption=category_description
            )

            categories.save()
            return redirect('category_management')
        except Exception as e:
            raise e

    return render(request, 'admin_panel/add_category.html')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def update_category(request, category_id):
    try:
        categories = category.objects.get(id=category_id)

        if request.method == 'POST':
            category_name = request.POST['category_name']
            category_slug = request.POST['category_slug']
            category_description = request.POST['category_description']

            categories.category_name = category_name
            categories.slug = category_slug
            categories.desciption= category_description

            categories.save()
            return redirect('category_management')

        context = {
            'category': categories,
        }
    except Exception as e:
        raise e

    return render(request, 'admin_panel/update_category.html', context)




@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def delete_category(request, category_id):
    categories = category.objects.get(id=category_id)
    categories.delete()

    return redirect('category_management')


#VARIATION MANAGEMENT 
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def variation_management(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        variations = Variation.objects.filter(Q(product__product_name__icontains=keyword) | Q(variation_category__icontains=keyword) | Q(variation_values__icontains=keyword)).order_by('id')

    else:
        variations = Variation.objects.all().order_by('id')

    paginator = Paginator(variations, 4)
    page = request.GET.get('page')
    paged_variations = paginator.get_page(page)

    context = {
        'variations': paged_variations
    }
    return render(request, 'admin_panel/variation_management.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def add_variation(request):

    if request.method == 'POST':
        form = VariationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('variation_management')

    else:
        form = VariationForm()

    context = {
        'form': form
    }
    return render(request, 'admin_panel/add_variation.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def update_variation(request, variation_id):
    variation = Variation.objects.get(id=variation_id)

    if request.method == 'POST':
        form = VariationForm(request.POST, instance=variation)
        if form.is_valid():
            form.save()
            return redirect('variation_management')

    else:
        form = VariationForm(instance=variation)

    context = {
        'variation': variation,
        'form': form
    }
    return render(request, 'admin_panel/update_variation.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def delete_variation(request, variation_id):
    variation = Variation.objects.get(id=variation_id)
    variation.delete()
    return redirect('variation_management')

#ADMIN ORDER
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def admin_order(request):
    current_user = request.user
    try:

        if request.method == 'POST':
            keyword = request.POST['keyword']
            orders = Order.objects.filter(Q(user=current_user), Q(is_ordered=True), Q(order_number__contains=keyword) | Q(user__email__icontains=keyword) | Q(first_name__startswith=keyword) | Q(last_name__startswith=keyword) | Q(phone__startswith=keyword)).order_by('-created_at')

        else:
            orders = Order.objects.filter(
                user=current_user, is_ordered=True).order_by('-created_at')
    except Exception as e:
        raise e
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
    }
    return render(request, 'admin_panel/admin_order.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_admin, login_url='home')
def admin_change_password(request):
    if request.method == 'POST':
        current_user = request.user
        current_password = request.POST['current_password']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if check_password(current_password, current_user.password):
                if check_password(password, current_user.password):
                    messages.warning(
                        request, 'Current password and new password is same')
                else:
                    hashed_password = make_password(password)
                    current_user.password = hashed_password
                    current_user.save()
                    messages.success(request, 'Password changed successfully')
            else:
                messages.error(request, 'Wrong password')
        else:
            messages.error(request, 'Passwords does not match')
    return render(request, 'admin_panel/admin_change_password.html')

