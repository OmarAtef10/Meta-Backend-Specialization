from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    slug = models.SlugField(blank=True, null=True)
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.title.replace(" ", "-").lower()
        super(Category, self).save(*args, **kwargs)


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    featured = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.user.username + " Cart"

    class Meta:
        unique_together = ('menuitem', 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(default=0, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField(db_index=True)

    def __str__(self):
        return self.user.username + " Order With ID " + str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

    def __str__(self):
        return self.order.user.username + " Order " + self.menuitem.title + " Item"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.unit_price = self.menuitem.price
        self.price = self.quantity * self.menuitem.price
        super(OrderItem, self).save(force_insert, force_update, using, update_fields)
