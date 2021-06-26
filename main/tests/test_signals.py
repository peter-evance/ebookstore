from django.test import TestCase
from django.core.files.images import ImageFile
from decimal import Decimal
from main import models


class TestSignal(TestCase):
    def test_thumbnails_are_generated_on_save(self):
        book = models.Book(
            name='Mitch Rap Book Series',
            price=Decimal('19.99')
        )
        book.save()
        with open(
                'main/fixtures/mitch-rap-book-series.jpg', 'rb') as f:
            image = models.BookImage(
                book=book,
                image=ImageFile(f, name='mrbs.jpg')
            )
            with self.assertLogs('main', level='INFO') as cm:
                image.save()

        self.assertGreaterEqual(len(cm.output), 1)
        image.refresh_from_db()

        with open(
                'main/fixtures/mitch-rap-book-series.jpg', 'rb') as f:
            expected_content = f.read()
            assert image.thumbnail.read() == expected_content

        image.thumbnail.delete(save=False)
        image.image.delete(save=False)
