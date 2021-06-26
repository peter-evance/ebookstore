from django.db import models


class Book(models.Model):
    '''Details of a particular book'''
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)


class BookImage(models.Model):
    '''Handles image(s) for a particular book/books'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book-images')
    thumbnail = models.ImageField(upload_to='book-thumbnails', null=True)


class BookTag(models.Model):
    '''Handles the concept of generalization into categories eg. science, romance'''
    books = models.ManyToManyField(Book, blank=True)
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
