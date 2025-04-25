from django.db import models
from django.utils import timezone
from users.models import User, Seller


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    allow_bargain = models.BooleanField(default=False)
    min_price = models.FloatField(null=True, blank=True)  # Minimum price for bargaining

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"

    class Meta:
        db_table = 'reviews'


class BargainRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('counter', 'Counter Offer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    offered_price = models.FloatField()
    counter_price = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bargain for {self.product.name} - {self.offered_price}"

    class Meta:
        db_table = 'bargain_requests'