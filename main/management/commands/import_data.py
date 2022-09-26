import os.path
import csv
from django.core.management.base import BaseCommand
from collections import Counter
from django.core.files.images import ImageFile
from django.template.defaultfilters import slugify
from main import models


class Command(BaseCommand):
    help = 'Import books in ebookstore'

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=open)
        parser.add_argument("image_basedir", type=str)

    def handle(self, *args, **options):
        self.stdout.write("Importing products...")
        c = Counter()
        reader = csv.DictReader(options.pop("csvfile"))
        for row in reader:
            book, created = models.Book.get_or_create(
                name=row["name"], price=row["price"]
            )
            book.description = row["description"]
            book.slug = slugify(row["name"])
            for import_tag in row["tags"].split("|"):
                tag, tag_created = models.BookTag.objects.get_or_create(
                    name=import_tag)
                book.tags.add(tag)
                c["tags"] += 1
                if tag_created:
                    c["tags_created"] += 1
            with open(os.path.join(options["image_basedir"], row["image_filename"]), "rb") as f:
                image = models.BookImage(
                    book=book, image=ImageFile(f, name=row["image_filename"]))
                image.save()
                c["images"] += 1
            book.save()
            c["books"] += 1
            if created:
                c["books_created"] += 1
        self.stdout.write("Books processed=%d (created=%d)" %
                          (c["books"], c["books_created"]))
        self.stdout.write("Tags processed=%d (created=%d)" %
                          (c["tags"], c["tags_created"]))
        self.stdout.write("Images processed=%d" % c["images"])
