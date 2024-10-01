from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    category_moto = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='products_category')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='products_images')
    price = models.IntegerField()
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    inventory = models.IntegerField(default=1)

    def __str__(self):
        return self.name


