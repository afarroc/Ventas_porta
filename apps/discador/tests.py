from django.test import TestCase
from .models import BaseLlamada


class BaseLlamadaModelTest(TestCase):
    def setUp(self):
        self.base = BaseLlamada.objects.create(
            telefono='123456789',
            nombres='Juan',
            paterno='Pérez',
            materno='García'
        )

    def test_base_creation(self):
        self.assertEqual(self.base.telefono, '123456789')
        self.assertTrue(str(self.base))
