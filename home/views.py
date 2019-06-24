from django.shortcuts import render, get_list_or_404
from home.models import *
from .forms import RegistrationForm, CommentForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages

from django.db.models import Q
from django.views.generic import CreateView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
from django.contrib.auth import authenticate, login, logout

import uuid
from django.core.mail import EmailMultiAlternatives

# Create your views here.

# Trang chủ tiến hành shopping

def index(request):
    if request.user.is_authenticated == True:
        cart = Cart.objects.update_or_create(user=request.user)
    if request.GET.get('q') != None:

        cateParents = Category.objects.filter(cate_parent_id=0)
        query = request.GET.get('q')
        if query:
            result = Product.objects.filter(Q(title__icontains=query))
        else:
            result = Product.objects.filter(status="Published")
        pages = Paginator(result, 10)
        pageNumber = request.GET.get('page', 1)
        featureItems = Product.objects.all()
        ds = []
        dem = Product.objects.all().count()
        for item in featureItems:
            if item.sale_price > 0:
                sale_off = item.price - (float(item.sale_price / 100) * item.price)
                listtemp = {}
                listtemp['id'] = item.id
                listtemp['sale'] = sale_off
                ds.append(listtemp)
        try:
            features = pages.page(pageNumber)
        except PageNotAnInteger:
             features = pages.page(1)
        except EmptyPage:
            features = pages.page(pages.num_pages)

        context = {
            'parents': cateParents,
            'pages': features,
            'featureItems': features,
            'dem': dem,
            'sale': ds,
        }
        return render(request, "home/shop.html", context)
    else:
        cateParents = Category.objects.filter(cate_parent_id=0)
        featureItems = Product.objects.all()
        dem = Product.objects.all().count()
        paginator = Paginator(featureItems, 2)
        ds = []
        for item in featureItems:
            if item.sale_price > 0:
                sale_off = item.price - (float(item.sale_price /100) * item.price)
                listtemp = {}
                listtemp['id'] = item.id
                listtemp['sale'] = sale_off
                ds.append(listtemp)
        pageNumber = request.GET.get('page', 1)
        try:
            features = paginator.page(pageNumber)
        except PageNotAnInteger:
            features = paginator.page(1)
        except EmptyPage:
            features = paginator.page(paginator.num_pages)
        context = {
            'parents': cateParents,
            'featureItems': features,
            'dem': dem,
            'sale': ds,
        }
        return render(request, "home/shop.html", context)


# Trang chủ nhưng được phân loại theo loại sản phẩm

def categoris(request, cate_id):
    cateParents = Category.objects.filter(cate_parent_id=0)
    featureItems = Product.objects.filter(category_id=cate_id)
    cate = Category.objects.get(id=cate_id)
    dem = Product.objects.filter(category_id=cate_id).count()
    paginator = Paginator(featureItems, 2)

    ds = []
    for item in featureItems:
        if item.sale_price > 0:
            sale_off = item.price - (float(item.sale_price /100) * item.price)
            listtemp = {}
            listtemp['id'] = item.id
            listtemp['sale'] = sale_off
            ds.append(listtemp)

    pageNumber = request.GET.get('page', 1)
    try:
        features = paginator.page(pageNumber)
    except PageNotAnInteger:
        features = paginator.page(1)
    except EmptyPage:
        features = paginator.page(paginator.num_pages)
    context = {
        'cate': cate,
        'parents': cateParents,
        'featureItems': features,
        'dem': dem,
        'sale': ds,
    }
    return render(request, 'home/shop.html', context)


#---------------
def getProd(request, product_id):
    prod = Product.objects.get(id=product_id)

    prodct = {
        'prod': prod,
    }
    return render(request, 'home/shop.html', prodct)
#-----------------



#Trang product

def products(request, product_id):
    str = "0"
    st = "0"
    cateParents = Category.objects.filter(cate_parent_id=0)

    prod1 = Product.objects.filter(pk=product_id)
    prod = get_object_or_404(Product, pk=product_id)
    for a in prod1:
        cate = Category.objects.get(id=a.category.id)

    form = CommentForm()
    if request.method == 'POST':
        if request.user.is_authenticated == True:
            cart = Cart.objects.get(user=request.user)
            order = OrderDetail.objects.filter(cart=cart)
            st = "1"
            for a in order:
                if a.item.id == product_id:
                    str = "1"
                    form = CommentForm(request.POST, author=request.user, product = prod)
                    if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(request.path)
    ds = []
    for item in prod1:
        if item.sale_price > 0:
            sale_off = item.price - (float(item.sale_price / 100) * item.price)
            listtemp = {}
            listtemp['id'] = item.id
            listtemp['sale'] = sale_off
            ds.append(listtemp)
        else:
            sale_off = item.price
            listtemp = {}
            listtemp['id'] = item.id
            listtemp['sale'] = sale_off
            ds.append(listtemp)

    prodct = {
        'str':str,
        'st':st,
        'parents': cateParents,
        'cate': 'None',
        'prod1': prod1,
        'prod': prod,
        'form': form,
        'sale': ds,
    }
    return render(request, 'home/product.html', prodct)

#-------------------
def product_cates(request, product_id, cate_id):

    cate = Category.objects.get(id=cate_id)
    prod1 = Product.objects.filter(pk=product_id)
    prod = get_object_or_404(Product, pk=product_id)

    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST, author=request.user, product=prod)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path)
    ds = []
    for item in prod1:
        if item.sale_price > 0:
            sale_off = item.price - (float(item.sale_price / 100) * item.price)
            listtemp = {}
            listtemp['id'] = item.id
            listtemp['sale'] = sale_off
            ds.append(listtemp)
        else:
            sale_off = item.price
            listtemp = {}
            listtemp['id'] = item.id
            listtemp['sale'] = sale_off
            ds.append(listtemp)

    prodct = {
        'prod1': prod1,
        'prod': prod,
        'form': form,
        'sale': ds,
        'cate': cate,
    }
    return render(request, 'home/product.html', prodct)
#-------------------

# Trang đăng ký tài khoản

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home')

    return render(request, 'home/dangky.html', {'form': form})

#Trang chủ với chức năng thêm vào giỏ hàng

@login_required
def add_to_cart(request):

      id =request.GET.get('id')
      user = request.GET.get('user')
      sl =  request.GET.get('soluong')
      us = CustomerUser.objects.get(pk=user)
      c = Cart.objects.get(user=us)
      a = CartItem.objects.filter(item=id,cart=c).count()
      d = Product.objects.get(pk=id)
      if int(d.inventory) >= int(sl):
            if a == 1:
                  soluong = CartItem.objects.get(item=id, cart=c)
                  soluong.quantity = int(sl)

                  if d.sale_price > 0:
                      soluong.total_price = int(soluong.quantity) * int(d.price - (float(d.sale_price / 100) * d.price))
                  else:
                      soluong.total_price = int(soluong.quantity) * int(d.price)
                  soluong.save()
                  return HttpResponse("Sản phẩm đã được thêm 1")
            else:
                  if d.sale_price > 0:
                    gia = int(sl) * int(d.price - (float(d.sale_price / 100) * d.price))
                  else:
                    gia = int(sl) * int(d.price)

                  CartItem.objects.create(cart=c, item=d, quantity=sl, total_price=gia)
                  return HttpResponse("Thêm thành công")
      else:
            return HttpResponse("Số Lượng không đủ")


#-------------------
def add_to_cart1(request, cate_id):
    cate = Category.objects.get(pk=cate_id)
    id = request.GET.get('id')
    user = request.GET.get('user')
    sl = request.GET.get('soluong')
    us = CustomerUser.objects.get(pk=user)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(item=id, cart=c).count()
    d = Product.objects.get(pk=id)
    if int(d.inventory) >= int(sl):
        if a == 1:
            soluong = CartItem.objects.get(item=id, cart=c)
            soluong.quantity = int(sl)

            if d.sale_price > 0:
                soluong.total_price = int(soluong.quantity) * int(d.price - (float(d.sale_price / 100) * d.price))
            else:
                soluong.total_price = int(soluong.quantity) * int(d.price)
            soluong.save()
            return HttpResponse("Sản phẩm đã được thêm 1")
        else:
            if d.sale_price > 0:
                gia = int(sl) * int(d.price - (float(d.sale_price / 100) * d.price))
            else:
                gia = int(sl) * int(d.price)

            CartItem.objects.create(cart=c, item=d, quantity=sl, total_price=gia)
            return HttpResponse("Thêm thành công")
    else:
        return HttpResponse("Số Lượng không đủ")
# -------------------

#Trang chủ với chức năng là xử lý số lượng

def show_cart(request):
    user = request.GET.get('ten')
    us = CustomerUser.objects.get(pk=user)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(cart=c).count()
    return HttpResponse(a,content_type='application/json')

#-------------------
def show_cart1(request, cate_id):
    cate = Category.objects.get(pk=cate_id)
    user = request.GET.get('ten')
    us = CustomerUser.objects.get(pk=user)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(cart=c).count()
    return HttpResponse(a,content_type='application/json')
#-------------------

#-------------------
def my_cart_cate(request, user_id, cate_id):
    cate = Category.objects.get(pk=cate_id)
    us = CustomerUser.objects.get(pk=user_id)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(cart=c)
    total = 0
    for carts in a:
        total += int(carts.total_price)
    context = {
        'total': total,
        'a': a,
    }
    return render(request, 'home/cart.html', context)
#-------------------


#-------------------
def my_cart_pro(request, user_id):

    us = CustomerUser.objects.get(pk=user_id)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(cart=c)
    total = 0
    for carts in a:

        total += int(carts.total_price)

    context = {
        'total': total,
        'a': a,
    }
    return render(request, 'home/cart.html', context)
#-------------------


#-------------------
def my_cart_pro_cate(request, user_id, cate_id):
    cate = Category.objects.get(pk=cate_id)
    us = CustomerUser.objects.get(pk=user_id)
    c = Cart.objects.get(user=us)
    a = CartItem.objects.filter(cart=c)
    context ={
        'a': a,
        'cate': cate,
    }
    return render(request, 'home/cart.html', context)
#-------------------


# Trang giỏ hàng với chức năng là xóa sản phẩm

def del_item(request, product_id):
    if request.user.is_authenticated == True:
        us = CustomerUser.objects.get(username = request.user)
        c = Cart.objects.get(user=us)
        item = CartItem.objects.get(id=product_id)
        item.delete()
        return HttpResponseRedirect('../')

#-------------------
def del_item_cate(request, cate_id, user_id, product_id):
    us = CustomerUser.objects.get(pk=user_id)
    cate = Category.objects.get(pk=cate_id)
    c = Cart.objects.get(user=us)
    item = CartItem.objects.get(id=product_id)
    item.delete()
    return HttpResponseRedirect('../')
#-------------------

#Trang giỏ hàng hiển thị tổng giá của tất cả sản phẩm

def trang403(request):
    return render(request,'home/trang403.html')

#Trang giỏ hàng
def total_cart(request):
    if request.user.is_authenticated == True:

        us = CustomerUser.objects.get(username=request.user)

        c = Cart.objects.get(user=us)
        cateParents = Category.objects.filter(cate_parent_id=0)
        a = CartItem.objects.filter(cart=c)
        total = 0

        tm = " "
        for carta in a:
            tp1 = carta.item.id
            tmp = Product.objects.get(pk=tp1)
            if int(tmp.inventory) < int(carta.quantity):
                carta.quantity = tmp.inventory
                if tmp.sale_price > 0:
                    carta.total_price = int(carta.quantity) * int(tmp.price - (float(tmp.sale_price / 100) * tmp.price))
                else:
                    carta.total_price = int(carta.quantity) * int(tmp.price)
                carta.save()
                tm += " "+tmp.title+", "

        for carts in a:
            total += int(carts.total_price)
        context = {
            'parents': cateParents,
            'total': total,
            'a': a,
            'us': us,
            'thongbao':tm
        }
        return render(request, 'home/cart.html', context)

# Tìm kiếm nhưng để cho vui, ở trên index có rồi hihi :)

def search(request):
    query = request.GET.get('q')
    if query:
        result = Product.objects.filter(Q(title__icontains=query))
    else:
        result = Product.objects.filter(status="Published")
    pages =Paginator(result, 10)
    pageNumber = request.GET.get('page', 1)
    try:
        features = pages.page(pageNumber)
    except PageNotAnInteger:
        features = pages.page(1)
    except EmptyPage:
        features = pages.page(pages.num_pages)
    context = {
        'featureItems': features,
        'pages': features,
    }
    return render(request, 'home/shop.html', context)

# Hiển thị trang thanh toán

def Order_vip(request):
    if request.user.is_authenticated == True:
        us = CustomerUser.objects.get(username=request.user)
        return render(request, 'home/thanhtoan.html', {'user': us})

#-------------------
def Order_vip_cate(request, user_id, cate_id):
    user = CustomerUser.objects.get(pk=user_id)
    cate = Category.objects.get(pk=cate_id)
    return render(request, 'home/thanhtoan.html', {'user': user, 'cate': cate})
#-------------------

# Chức năng thêm phương thức thanh toán

def Order_Cart(request):
    if request.user.is_authenticated == True:
        address_ship = request.GET.get('diachi')
        desciption = request.GET.get('ghichu')
        hoten = request.GET.get('hoten')
        sdt = request.GET.get('sdt')
        us = CustomerUser.objects.get(username=request.user)
        cart1 = Cart.objects.get(user=us)
        items = CartItem.objects.filter(cart=cart1)
        total = 0
        for cartitem in items:
            total += int(cartitem.total_price)
            products_it = cartitem.item
            products_it.inventory = int(products_it.inventory) - int(cartitem.quantity)
            products_it.save()
            OrderDetail.objects.create(cart=cartitem.cart, item=cartitem.item, quantity=cartitem.quantity, total_price=cartitem.total_price)
            CartItem.objects.filter(cart=cart1).delete()
        Order.objects.create(user=us, cart=cart1,full_name=hoten,phone_number=sdt, shipping_address=address_ship, order_description=desciption, total_order=total)

        context = {
            'total': total,
            'items': items,
        }
        return render(request, 'home/hoadon.html', context)


# Hiển thị thông báo thanh toán thành công

def Order_Success(request, user_id):
    user = CustomerUser.objects.get(pk=user_id)
    cart = Cart.objects.get(user=user)
    items = CartItem.objects.filter(cart=cart)
    total = 0
    for cartitem in items:
        total += int(cartitem.total_price)
    context = {
        'total': total,
        'items': items,
    }
    return HttpResponse("Đây là hóa đơn")

# Trang giỏ hàng với chức năng thay đổi số lượng sản phẩm

def thaydoisoluong(request):
    soluong = request.GET.get('soluong')
    sanpham = request.GET.get('idsp')
    iduser = request.GET.get('idus')
    product1 =Product.objects.get(pk=sanpham)
    if int(soluong) <= int(product1.inventory) :
        user = CustomerUser.objects.get(pk=iduser)
        carts =  Cart.objects.get(user=user)
        cartit = CartItem.objects.get(item=product1,cart=carts)
        cartit.quantity = int(soluong)
        if product1.sale_price > 0:
            cartit.total_price = int(soluong)* int(product1.price - (float(product1.sale_price / 100) * product1.price))
            cartit.save()
            a = "cập nhật thành công"
        else:
            cartit.total_price = int(soluong) * int(product1.price)
            cartit.save()
            a= "cập nhật thành công"
    else:
        a="số lượng tồn không đủ"
    return HttpResponse(a)

#Trang dành cho shipper

def ShowListShip(request):
    return render(request, 'home/temp.html')

def ListShip(request, user_id):
    userid = CustomerUser.objects.get(pk=user_id)
    order = Shipment.objects.filter(shipper=userid)
    context = {
            'order': order,
        }
    return render(request, 'home/ShipList.html', context)

def ShipDetail(request, user_id, order_id):
    if request.GET.get('completed') != None:
        userid = CustomerUser.objects.get(pk=user_id)
        # a = Order.objects.filter(id=order_id)
        orders = Order.objects.get(id=order_id)
        # b = Shipment.objects.get(shipper=user_id)
        order = Shipment.objects.filter(shipper=userid, order=orders)
        cart = Cart.objects.get(pk=orders.cart.id)
        product = OrderDetail.objects.filter(cart=cart)
        completed = request.GET.get('completed')
        if completed == 1:
           completed = True
        orders.is_completed = completed
        orders.save()
        context = {
                'cart':cart,
                'orders': orders,
                'order': order,
                'product': product,
                'temp': "1"
            }
        return render(request, 'home/chitietdonhang.html', context)
    else:
        userid = CustomerUser.objects.get(pk=user_id)
        # a = Order.objects.filter(id=order_id)
        orders = Order.objects.get(id=order_id)

        # b = Shipment.objects.get(shipper=user_id)
        order = Shipment.objects.filter(shipper=userid, order=orders)
        cart = Cart.objects.get(pk=orders.cart.id)
        product = OrderDetail.objects.filter(cart=cart)
        context = {
            'cart': cart,
            'orders': orders,
            'order': order,
            'product': product,
            'temp':"0"
        }
        return render(request, 'home/chitietdonhang.html', context)


def registership(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/shipment/login')

    return render(request, 'home/dangky.html', {'form': form})


def send_email(request):
    if request.GET.get('user_name') != None:
        taikhoan = CustomerUser.objects.all()
        for temp in taikhoan:
            if temp.username == request.GET.get('user_name'):
                a = uuid.uuid4().hex[:6].upper()
                request.session['code'] = a
                request.session['us'] = temp.id
                request.session.set_expiry(160);
                subject, from_email, to = 'Xát Nhận Tài Khoản', 'demo1hacker@gmail.com', temp.email
                text_content = 'This is an important message.'
                html_content = '<h4> xin chào ' + to + '</h4>' + '<div>Đây là mã xát nhận  của bạn mã có hiệu lực trong 60s</div><p></p> <div style="background-color: #0000FF;font-size: 40px;width: 200px;height: auto;text-align: center" >' + a + '</div>'
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                # subject = 'Công Ty Đa Cấp'
                # message = '<h1> mã code Của Bạn </h1>:'+a;
                # from_email = request.POST.get('from_email')
                # send_mail(subject, message, 'demo1hacker@gmail.com', ['kingminhluan9@gmail.com'],fail_silently=False)
                return HttpResponse('Vui Lòng kiểm tra mail')
    if request.GET.get('from_email') != None:
        a = uuid.uuid4().hex[:6].upper()
        request.session['code'] = a
        request.session.set_expiry(60);
        subject, from_email, to = 'Xát Nhận Tài Khoản', 'demo1hacker@gmail.com', request.GET.get('from_email')
        text_content = 'This is an important message.'
        html_content = '<h4> xin chào ' + to + '</h4>' + '<div>Đây là mã xát nhận  của bạn mã có hiệu lực trong 60s</div><p></p> <div style="background-color: #0000FF;font-size: 40px;width: 200px;height: auto;text-align: center" >' + a + '</div>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # subject = 'Công Ty Đa Cấp'
        # message = '<h1> mã code Của Bạn </h1>:'+a;
        # from_email = request.POST.get('from_email')
        # send_mail(subject, message, 'demo1hacker@gmail.com', ['kingminhluan9@gmail.com'],fail_silently=False)
        return HttpResponse('Vui Lòng kiểm tra mail')


def kiemtracode(request):
    if request.GET.get('macode') == request.session.get('code'):
        a = uuid.uuid4().hex[:6].upper()
        b = request.session.get('code')
        c = a + b
        request.session['nn'] = c
        return HttpResponse('1' + c)
    else:
        return HttpResponse('0')


def doimatkhau(request, code):
    c='1'
    t =  request.session.get('nn')
    t =t+c
    if code == t:
        if request.POST.get('txtmk') != None:
            tmp = request.session.get('nn')
            tk = tmp[6]
            taikhoan = CustomerUser.objects.get(pk=int(tk))
            taikhoan.password = request.POST.get('txtmk')
            taikhoan.save()
            return render(request, "home/doimatkhau.html")
        else:
            return render(request, "home/shop.html")
    else:
        return render(request, "home/doimatkhau.html")