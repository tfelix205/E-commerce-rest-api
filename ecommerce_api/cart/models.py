from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from users.models import User


# Create your models here.
class Cart(models.Model):
    """Shopping cart model"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        ordering = ['-updated_at']
        
    def __str__(self):
        return F"cart for {self.user.email}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Calculate cart total (can add taxes, shipping later)"""
        return self.total
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
        
        
class CartItem(models.Model):
    """Cart item model"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        ordering = ['-created_at']
        unique_together = ('cart', 'product')
        
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def total_price(self):
        """Calculate the total price for this item"""
        return self.product.price * self.quantity
    
    def clean(self):
        """Validate cart item"""
        from django.core.exceptions import ValidationError
        
        if self.product.stock < self.quantity:
            raise ValidationError(
                f"Only {self.product.stock} units available for {self.product.name}"
            )
            
    def save(self, *args, **kwargs):
        """Override save to validate stock"""
        self.clean()
        super().save(*args, **kwargs)