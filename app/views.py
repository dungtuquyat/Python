from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse,JsonResponse
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages


def detail(request):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        user_not_login="hidden"
        user_login="show"

    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems=order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    id=request.GET.get('id','')
    products=Product.objects.filter(id=id)
    context={'items':items,'order':order,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'products':products}
    return render(request,'app/detail.html',context)

def category(request):
    if request.user.is_authenticated:
            customer=request.user
            order,created=Order.objects.get_or_create(customer=customer,complete=False)
            items=order.orderitem_set.all()
            cartItems=order.get_cart_items
    else:
            order={'get_cart_items':0,'get_cart_total':0}
            cartItems=order['get_cart_items']
    categories=Category.objects.filter(is_sub=False)
    active_category=request.GET.get('category','')
    if active_category:
        products=Product.objects.filter(category__slug=active_category)
    context={'categories':categories,'active_category':active_category,'products':products,'cartItems':cartItems}        
    return render(request,'app/category.html',context)    
# Create your views here.
def search(request):
    searched = ""
    keys = []
    if request.method=="POST":
        searched=request.POST["searched"]
        keys=Product.objects.filter(name__contains=searched)
        
    if request.user.is_authenticated:
            customer=request.user
            order,created=Order.objects.get_or_create(customer=customer,complete=False)
            items=order.orderitem_set.all()
            cartItems=order.get_cart_items
    else:
            
            order={'get_cart_items':0,'get_cart_total':0}
            cartItems=order['get_cart_items']
    products=Product.objects.all()
    categories=Category.objects.filter(is_sub=False)
    return render(request,'app/search.html',{"searched":searched,"keys":keys,'products':products,'cartItems':cartItems,'categories':categories})

def register(request):
    user_not_login="show"
    user_login="hidden"
    form=CreateUserForm()
    context={'form':form}
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')    
    context={'form':form,'user_not_login':user_not_login,'user_login':user_login}        
    return render(request,'app/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:messages.info(request,'user or password not correct')
    categories=Category.objects.filter(is_sub=False)    
    user_not_login="show"
    user_login="hidden"
     
    context={'user_not_login':user_not_login,'user_login':user_login,'categories':categories}
    return render(request,'app/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        user_not_login="hidden"
        user_login="show"
    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems=order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    context={'items':items,'order':order}
    products=Product.objects.all()
    categories=Category.objects.filter(is_sub=False)
    context={'products':products,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories}
    return render(request,'app/home.html',context)

def cart(request):
    if request.user.is_authenticated:
        categories=Category.objects.filter(is_sub=False)
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        
        cartItems=order.get_cart_items
        user_not_login="hidden"
        user_login="show"

    else:
        categories=Category.objects.filter(is_sub=False)
        items=[]
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems=order['get_cart_items']
        user_not_login="show"
        user_login="hidden"

    context={'items':items,'order':order,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories}
    return render(request,'app/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        user_not_login="hidden"
        user_login="show"

    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0}
        cartItems=order['get_cart_items']
        user_not_login="show"
        user_login="hidden"

    context={'items':items,'order':order,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login}
    return render(request,'app/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user

    product = Product.objects.get(id=productId)

    # Kiểm tra đơn hàng chưa hoàn thành
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Nếu đơn hàng hiện tại đã hoàn thành, tạo một đơn hàng mới
    if order.complete:
        order = Order.objects.create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)

def completeOrder(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer = request.user
        
        address = data['address']
        city = data['city']
        state = data['state']
        mobile = data['mobile']
    

        # Lấy đơn hàng chưa hoàn thành của khách hàng
        order = Order.objects.get(customer=customer, complete=False)

        # Cập nhật hoặc tạo mới thông tin vận chuyển
        shipping_address, created = ShippingAddress.objects.get_or_create(
            customer=customer,
            order=order,
            defaults={
                'address': address,
                'city': city,
                'state': state,
                'mobile': mobile,
            }
        )

        if not created:
            shipping_address.address = address
            shipping_address.city = city
            shipping_address.state = state
            shipping_address.mobile = mobile
            shipping_address.save()

        # Cập nhật trạng thái đơn hàng thành hoàn thành
        order.complete = True
        order.save()

        return JsonResponse('Order completed', safe=False)
    return JsonResponse('Invalid request', safe=False)