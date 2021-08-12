from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator
import logging

logger= logging.getLogger(__name__)

class UserManager(BaseUserManager):
    use_in_migrations = True

    # Due to the conflicting syntax the naming takes underscore to differentiate them
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff set to True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser set to True."
            )
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    @property
    def is_employee(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Employees").exists()
        )
    
    @property
    def is_dispatcher(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Dispatchers").exists()
            )


class BookTagMananager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class BookTag(models.Model):
    '''Handles the concept of generalization into categories eg. science, romance'''
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = BookTagMananager()

    # Returns human readable string on the admin dashboard.
    def __str__(self):
        return self.name

    # Allows possibility of running dumpdata using natural keys instead of internal database keys
    def natural_key(self):
        return self.slug


class BookManager(models.Manager):
    '''Extends the functionality of default model object manager'''

    def active(self):
        return self.filter(active=True)


class Book(models.Model):
    '''Details of a particular book'''
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    tags = models.ManyToManyField(BookTag, blank=True)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = BookManager()

    def __str__(self):
        return self.name


class BookImage(models.Model):
    '''Handles image(s) for a particular book/books'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book-images')
    thumbnail = models.ImageField(upload_to='book-thumbnails', null=True)


class Address(models.Model):
    SUPPORTED_COUNTIES =(
        ('ksm', 'Kisumu'),
        ('nrb', 'nairobi'),
        ('mbm', 'Mombasa')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField("Address line 1", max_length=60)
    address2 = models.CharField("Address line 2", max_length=60, blank=True)
    zip_code = models.CharField("ZIP / Postal code", max_length=12)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=3, choices=SUPPORTED_COUNTIES)
    
    
    def __str__(self):
        return ", ".join(
            [
                self.name,
                self.address1,
                self.address2,
                self.zip_code,
                self.city,
                self.country,
            ]
            )
        
class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = (
        (OPEN, "Open"),
        (SUBMITTED, "Submitted")
        )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
        )
    status = models.IntegerField(choices=STATUSES, default=OPEN)
    
    def is_empty(self):
        return self.basketline_set.all().count() == 0
    
    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())
    
class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    
class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (PAID, "Paid"), (DONE, "Done"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60,blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_county = models.CharField(max_length=3)
    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_county = models.CharField(max_length=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise exceptions.BasketException(
                "Cannot create order without user"
                )
        logger.info(
            "Creating order for basket_id=%d",
            "shipping_address_id=%d", 
            "billing_address_id=%d",
            self.id,
            shipping_address.id,
            billing_address.id,
            )
        order_data = {
            "user":self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zip_code": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country,
            }
        order = Order.objects.create(**order_data)
        c=0
        for line in self.basketline_set.all():
            for item in range(line.quantity):
                order_line_data = {
                    "order": order,
                    "product": line.product,
                    }
                order_line = OrderLine.objects.create(
                    **order_line_data
                    )
                c += 1
                logger.info(
                    "Created order with id=%d and lines_count=%d",
                    order.id,c,
                    )
        self.status = Basket.SUBMITTED
        self.save()
        return order
    
class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = (
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (SENT, "Sent"),
        (CANCELLED, "Cancelled"),
        )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="lines"
        )
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT
        )
    status = models.IntegerField(choices=STATUSES, default=NEW)