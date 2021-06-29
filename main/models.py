from django.db import models


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
