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

    @property
    def cartTotal(self):
        items = CartItem.objects.filter(cart=self.pk)
        total = 0
        for item in items:
            total += item.total
        return total

    def __str__(self):
        return self.user.username + " Cart"

    class Meta:
        unique_together = ('user',)
    # class Meta:
    #     unique_together = ('menuitem', 'user')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def total(self):
        return self.menuitem.price * int(self.quantity)

    def __str__(self):
        return f'{self.cart.pk} - {self.menuitem.title}'

    class Meta:
        unique_together = ('menuitem', 'cart')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(default=0, db_index=True)
    date = models.DateField(db_index=True, auto_now_add=True)

    @property
    def orderTotal(self):
        items = OrderItem.objects.filter(order=self.pk)
        total = 0
        for item in items:
            total += item.price
        return total

    def __str__(self):
        return self.user.username + " Order With ID " + str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
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
