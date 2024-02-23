from itertools import count
import json
from django.shortcuts import get_object_or_404, render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from datetime import datetime
from django.conf import settings
from .models import Cartlist


def home_view(request):
    products=models.Product.objects.all()
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})
    


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        customername = models.User.objects.get(id = order.customer_id)
        order.customername = customername
        orderlist = str(order.product).replace('[','').replace(']','').replace("'",'')
        orderlist = orderlist.split(',')
        orderlist = [int(x.strip()) for x in orderlist]
        for ids in orderlist:
            ordered_product=models.Product.objects.all().filter(id=ids)
        ordered_by=models.Customer.objects.all().filter(id = order.customer_id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})

def admin_categories_view(request):
    categories=models.Category.objects.all()
    return render(request,'ecom/admin_category.html',{'categories':categories})


def admin_add_category(request):
    categoryForm=forms.CategoryForm()
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST, request.FILES)
        if categoryForm.is_valid():
            categoryForm.save()
        return redirect('admin-categories')
    return render(request,'ecom/admin_add_category.html',{'categoryForm':categoryForm})

def delete_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-categories')


@login_required(login_url='adminlogin')
def update_category_view(request, pk):
    category = models.Category.objects.get(id=pk)
    categoryForm = forms.CategoryForm(instance=category)
    
    if request.method == 'POST':
        categoryForm = forms.CategoryForm(request.POST, instance=category)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-categories')  
    
    return render(request, 'ecom/admin_update_category.html', {'categoryForm': categoryForm})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    category = models.Category.objects.all()
    print(category)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm,'category':category})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    category = models.Category.objects.all()
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm, 'category':category})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    print(product_count_in_cart)
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        customername = models.User.objects.get(id = order.customer_id)
        order.customername = customername
        orderlist = str(order.product).replace('[','').replace(']','').replace("'",'')
        orderlist = orderlist.split(',')
        orderlist = [int(x.strip()) for x in orderlist]
        for ids in orderlist:
            ordered_product=models.Product.objects.all().filter(id=ids)
        ordered_by=models.Customer.objects.all().filter(id = order.customer_id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})

def view_products(request,pk):
    ordersdet = models.Orders.objects.get(id = pk)
    orderlist = str(ordersdet.product).replace('[','').replace(']','').replace("'",'')
    values = map(int, orderlist.rstrip(',').split(','))
    ordered_product=models.Product.objects.all().filter(id__in=values)
    return render(request,'ecom/view_products.html',{'products':ordered_product})
@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products_data = []
    products=models.Product.objects.all().filter(name__icontains=query)
    products_data.append({'productsss': products})
    context = {'products_data': products_data} 
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart,'context':context,'query':query})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()
    category=models.Category.objects.all()
    products_data = []
    for categories in category:
        productsss = models.Product.objects.filter(category_id=categories.id)
        products_data.append({'category_name': categories.category_name,'category_id':categories.id,'productsss': productsss})
        context = {'products_data': products_data} 
        print(context) 
    #for cart counter, fetching products ids added by customer from cookies
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    response = render(request, 'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart,'context':context})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response



# for checkout of cart
def cart_view(request):
    #for cart counter
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()

    cartdetail = Cartlist.objects.filter(user_id=request.user.id)
    products_data = []
    grandtot = 0
    for categories in cartdetail:
        productsss = models.Product.objects.filter(id=categories.product_id)
        grandtot+=categories.finalprice
        products_data.append({'cart_id':categories.id,'quantity': categories.quantity,'totalamt':categories.finalprice,'productsss': productsss})
    context = {'products_data': products_data}    
    product_ids = []
    for ct in cartdetail:
        product_ids.append(ct.product_id)
    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    # product_id_in_cart=product_ids.split('|')
    products=models.Product.objects.all().filter(id__in = product_ids)
    for p in products:
        total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart,"context":context,'grandtot':grandtot})


def remove_from_cart_view(request,pk):
    #for counter in cart
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    remove_cart_lt = Cartlist.objects.model(id=pk)
    remove_cart_lt.delete()
    cartdetail = Cartlist.objects.filter(user_id=request.user.id)
    products_data = []
    grandtot = 0
    for categories in cartdetail:
        productsss = models.Product.objects.filter(id=categories.product_id)
        grandtot+=categories.finalprice
        products_data.append({'cart_id':categories.id,'quantity': categories.quantity,'totalamt':categories.finalprice,'productsss': productsss})
    context = {'products_data': products_data}    
    product_ids = []
    for ct in cartdetail:
        product_ids.append(ct.product_id)
    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    # product_id_in_cart=product_ids.split('|')
    products=models.Product.objects.all().filter(id__in = product_ids)
    for p in products:
        total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart,"context":context,'grandtot':grandtot})


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    category=models.Category.objects.all()
    products_data = []
    for categories in category:
        productsss = models.Product.objects.filter(category_id=categories.id)
        products_data.append({'category_name': categories.category_name,'category_id':categories.id,'productsss': productsss})
    context = {'products_data': products_data}    
    product_count_in_cart= Cartlist.objects.filter(user_id=request.user.id).count()
    return render(request,'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart,'category':category,'context':context,'query':""})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart = False
    product_count_in_cart = Cartlist.objects.filter(user_id=request.user.id).count()
    if product_count_in_cart != 0:
        product_in_cart = True
    
    # for counter in cart
    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            
            # for showing total price on payment page
            total = 0
            cartdetail = Cartlist.objects.filter(user_id=request.user.id)
            product_ids = []
            for ct in cartdetail:
                product_ids.append(ct.product_id)
            products = models.Product.objects.filter(id__in=product_ids)
            for p in products:
                total += p.price
            
            current_date = datetime.now().date()
            
            # Debugging print statements
            print("User ID:", request.user.id)
            print("Product IDs:", product_ids)
            
            # Create or get Orders object
            ordercrate, created = models.Orders.objects.get_or_create(
                email=email,
                address=address,
                mobile=mobile,
                order_date=current_date,
                status='Pending',
                customer_id=request.user.id,
                product=product_ids
            )
            print("Order crate:", ordercrate)
            print("Created:", created)
            cart_objects = models.Cartlist.objects.filter(user_id=request.user.id)
            cart_objects.delete()
            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
    
    return render(request, 'ecom/customer_address.html', {'addressForm': addressForm, 'product_in_cart': product_in_cart, 'product_count_in_cart': product_count_in_cart})




# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,product=product,status='Pending',email=email,mobile=mobile,address=address)

    # after order placed cookies should be deleted
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})
 



# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    mydict={
        'orderDate':order.order_date,
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':order.status,
        'productName':product.name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':product.description,

    }
    return render_to_pdf('ecom/download_invoice.html',mydict)


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})


def cart_list(request):
    price = request.POST.get('price')
    quantity = request.POST.get('quantity')
    product_id = request.POST.get('product_id')
    finalprice = int(quantity) * int(price)
    status =1
    user_id = request.user.id
    getcart = Cartlist.objects.filter(user_id=user_id,product_id=product_id).count()
    if(getcart == 0):
        cart_item =Cartlist(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
            finalprice=finalprice,  # Assuming finalprice is the same as price initially
            status=status
        )
    
    # Save the new cart item to the database
        cart_item.save()
        cart_count = Cartlist.objects.filter(user_id=user_id).count()
        response_data = {
            'status': 1,
            'message': "Cart item saved successfully!",
            'count': cart_count
        }
        return JsonResponse(response_data)
    else:
        getcartup = Cartlist.objects.filter(user_id=user_id,product_id=product_id)
        cart_count = Cartlist.objects.filter(user_id=user_id).count()
        user_id = request.user.id
        cart_update = get_object_or_404(Cartlist, user_id=user_id, product_id=product_id)
        cart_update.quantity = request.POST.get('quantity')
        cart_update.price = request.POST.get('price')
        cart_update.finalprice = int(request.POST.get('quantity')) * int(request.POST.get('price'))
        cart_update.status = 1
        cart_update.save()
        response_data = {
            'status': 0,
            'message': "This product updated cart successfully!!",
            'count': cart_count
        }
        return JsonResponse(response_data)
    
def update_cart(request):
    product_id = request.POST.get('product_id')
    user_id = request.user.id
    cart_instance = Cartlist.objects.filter(user_id=user_id, product_id=product_id).first()  # Get single instance
    if cart_instance:
        quantity = int(request.POST.get('quantity'))
        price = cart_instance.price
        final_price = quantity * price
        status = 1
        cart_instance.quantity = quantity
        cart_instance.price = price
        cart_instance.finalprice = final_price
        cart_instance.status = status
        cart_instance.save()
        response_data = {
            'status': 0,
            'message': "This product updated cart successfully!!",
        }
    else:
        response_data = {
            'status': 1,
            'message': "No cart entry found for the given product and user.",
        }
    return JsonResponse(response_data)
    
    