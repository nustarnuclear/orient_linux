from django.test import TestCase

# Create your tests here.

from calculation.models import PreRobinTask

class PreRobinTaskMethodTests(TestCase):
    def test_generate_pin_databank_xml(self):
        p=PreRobinTask.objects.first()
        p.generate_pin_databank_xml()