from xml.etree import cElementTree as ET
from unittest import TestCase

import dmarc
from .config import filename, sample_dir, Session

class TestGz(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        cls.file = f'{sample_dir}/{filename}'

        with open(cls.file, 'rb') as f:
            cls.file_bytes = f.read()

    def setUp(self):
        self.parser = dmarc.Parser()

    def test_default_tolerance(self):
        self.assertEqual(self.parser.tolerance, 'minimal')

    def test_default_schema(self):
        self.assertEqual(
            self.parser.schema.url.split('/')[-1], 'minimal_v01.xsd')

    def test_set_tolerance(self):
        self.parser.set_tolerance('relaxed')
        self.assertEqual(self.parser.tolerance, 'relaxed')

    def test_set_tolerance_schema(self):
        self.parser.set_tolerance('relaxed')
        self.assertEqual(
            self.parser.schema.url.split('/')[-1], 'relaxed_v01.xsd')

    def test_validate_file(self):
        self.parser.set_tolerance('relaxed')
        self.assertTrue(self.parser.validate(self.file))

    def test_validate_bytes(self):
        self.parser.set_tolerance('relaxed')
        self.assertTrue(self.parser.validate(self.file_bytes))

    def test_parse_from_file(self):
        doc = self.parser.from_file(self.file)
        self.assertIsInstance(doc, ET.Element)

    def test_parse_from_bytes(self):
        doc = self.parser.from_bytes(self.file_bytes)
        self.assertIsInstance(doc, ET.Element)

    def test_report_instance_file(self):
        doc = self.parser.from_file(self.file)
        report = dmarc.Report(doc)
        self.assertIsInstance(report, dmarc.Report)

    def test_report_instance_bytes(self):
        doc = self.parser.from_bytes(self.file_bytes)
        report = dmarc.Report(doc)
        self.assertIsInstance(report, dmarc.Report)

    def test_insert_report_file(self):
        doc = self.parser.from_file(self.file)
        report = dmarc.Report(doc)
        report.insert(self.session)

    def test_insert_report_bytes(self):
        doc = self.parser.from_bytes(self.file_bytes)
        report = dmarc.Report(doc)
        report.insert(self.session)

    def test_validation_exception_file(self):
        self.parser.set_tolerance('strict')
        self.assertRaises(
            dmarc.exceptions.ValidationError,
            self.parser.from_file, self.file)

    def test_validation_exception_bytes(self):
        self.parser.set_tolerance('strict')
        self.assertRaises(
            dmarc.exceptions.ValidationError,
            self.parser.from_bytes, self.file_bytes)
