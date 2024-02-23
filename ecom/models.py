from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name


class Product(models.Model):
    name=models.CharField(max_length=40)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.PositiveIntegerField()
    finalprice = models.DecimalField(max_digits=10, decimal_places=2)
    description=models.CharField(max_length=40)
    category_id = models.CharField(max_length=40)
    discount_type = models.CharField(max_length=40,null=True,blank=True)
    discount = models.CharField(max_length=40,null=True,blank=True)
    def __str__(self):
        return self.name
    

class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer_id=models.CharField(max_length=500,null=True)
    product=models.CharField(max_length=500,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
    

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name
    
class Cartlist(models.Model):
    user_id = models.CharField(max_length=20)
    product_id = models.CharField(max_length=20)
    quantity = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    finalprice = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    
