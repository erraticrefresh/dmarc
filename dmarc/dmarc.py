from xml.etree import ElementTree as ET
from gzip import open as gzip_open, BadGzipFile, decompress
from uuid import uuid4
from pathlib import Path

from logging import getLogger

from xmlschema import XMLSchema11

import dmarc.exceptions as exceptions

logger = getLogger()

pkg = Path(__file__).parent.absolute()

XSD_FILES = {
    'minimal': f'{pkg}/minimal_v01.xsd',
    'relaxed': f'{pkg}/relaxed_v01.xsd',
    'strict': f'{pkg}/rfc7489.xsd'}

class Parser:
    def __init__(self, tolerance='minimal'):

        self.tolerance = tolerance
        try:
            # rfc7489 schema uses XSD v1.1
            # https://www.w3.org/TR/xmlschema11-1/
            self.schema = XMLSchema11(XSD_FILES[tolerance])
        except:
            raise ValueError(
                "tolerance must be 'minimal', 'relaxed', or 'strict'")

    def _parse(self, data):
        try:
            # from .gz bytes
            data = decompress(data).decode()
        except BadGzipFile:

            # if not .gz, .xml bytes
            data = data.decode()

        if not self.schema.is_valid(data):
            raise exceptions.ValidationError

        doc = ET.fromstring(data)

        return doc

    def from_file(self, fp):
        """
        Parse XML from gzip or xml file
        Arguments:
            fp (str): filepath
        """
        try:
            with open(fp, 'rb') as f:
                data = f.read()

            doc = self._parse(data)

        except Exception as e:
            logger.log(logger.level, [e, fp])
            raise e

        return doc


    def from_bytes(self, data):
        """
        Parse XML from gzip or xml file bytes

        Arguments:
            data (bytes): bytes file object
        """

        try:
            doc = self._parse(data)

        except Exception as e:
            logger.log(logger.level, [e, data])
            raise e

        return doc

    def validate(self, src):
        """
        Validate xml report elements

        """
        try:
            if isinstance(src, bytes):
                src = src.decode()

            elif isinstance(src, str):
                if src.endswith('.gz'):
                    with gzip_open(src, 'rb') as f:
                        return self.schema.is_valid(f.read().decode())
                else:
                    return self.schema.is_valid(src)

        except Exception as e:
            logger.log(logger.level, [e, src])

class Report:
    """
    Extract the DMARC metadata as defined here:
    https://tools.ietf.org/html/rfc7489 in Appendix C
    If no data is found, return NA

    Arguments:
        doc (obj): ElementTree class instance
    """
    def __init__(self, doc):
        self.version = doc.findtext('version')
        self.metadata = Metadata(doc)
        self.policy_published = PolicyPublished(doc)
        self.records = [Record(elem) for elem in doc.findall('record')]

class Metadata:
    def __init__(self, doc):

        self.org_name = doc.findtext(
            'report_metadata/org_name', default='NA')
        self.email = doc.findtext(
            'report_metadata/email', default='NA')
        self.extra_contact_info = doc.findtext(
            'report_metadata/extra_contact_info', default='NA')
        self.report_id = doc.findtext(
            'report_metadata/report_id', default='NA')

        self.date_begin = doc.findtext(
            'report_metadata/date_range/begin', default='NA')
        self.date_begin = int(self.date_begin) \
            if self.date_begin.isdigit() else 0

        self.date_end = doc.findtext(
            'report_metadata/date_range/end', default='NA')
        self.date_end = int(self.date_end) \
            if self.date_end.isdigit() else 0

        self.errors = [e for e in doc.findall('report_metadata/error')]

class PolicyPublished:
    def __init__(self, doc):

        self.domain = doc.findtext('policy_published/domain', default='NA')
        self.adkim = doc.findtext('policy_published/adkim', default='NA')
        self.aspf = doc.findtext('policy_published/aspf', default='NA')
        self.p = doc.findtext('policy_published/p', default='NA')
        self.pct = doc.findtext('policy_published/pct', default='NA')
        self.fo = doc.findtext('policy_published/fo', default='NA')
        self.rf = doc.findtext('policy_published/rf', default='NA')
        self.ri = doc.findtext('policy_published/ri', default='NA')
        self.rua = doc.findtext('policy_published/rua', default='NA')
        self.ruf = doc.findtext('policy_published/ruf', default='NA')
        self.v = doc.findtext('policy_published/v', default='NA')

class Record:
    def __init__(self, rec):

        self.source_ip = rec.findtext('row/source_ip', default='NA')

        self.count = rec.findtext('row/count', default='NA')
        self.count = int(self.count) if self.count.isdigit() else 0

        self.disposition = rec.findtext(
            'row/policy_evaluated/disposition', default='NA')
        self.dkim = rec.findtext(
            'row/policy_evaluated/dkim', default='NA')
        self.spf = rec.findtext(
            'row/policy_evaluated/spf', default='NA')
        self.type = rec.findtext(
            'row/policy_evaluated/reason/type', default='NA')
        self.comment = rec.findtext(
            'row/policy_evaluated/reason/comment', default='NA')
        self.header_from = rec.findtext(
            'identifiers/header_from', default='NA')
        self.envelope_from = rec.findtext(
           'identifiers/envelope_from', default='NA')
        self.dkim_domain = rec.findtext(
            'auth_results/dkim/domain', default='NA')
        self.dkim_result = rec.findtext(
            'auth_results/dkim/result', default='NA')
        self.dkim_hresult = rec.findtext(
            'auth_results/dkim/human_result', default='NA')
        self.spf_domain = rec.findtext(
            'auth_results/spf/domain', default='NA')
        self.spf_result = rec.findtext(
            'auth_results/spf/result', default='NA')

def insert_report(report, session):
    """
    Insert DMARC Aggregate Report into database

    Arguments:
        report (obj): Report instance
        session (obj): SQLAlchemy session instance
    """

    uid = uuid4()
    errors = " | ".join(report.metadata.errors) \
        if report.metadata.errors else "NA"

    queries = []

    queries.append(f"""
    INSERT INTO report_metadata(
    uid, organization, email, extra_contact_info,
    report_id, date_begin, date_end, `errors`)
    VALUES('{uid}', '{report.metadata.org_name}',
    '{report.metadata.email}', '{report.metadata.extra_contact_info}',
    '{report.metadata.report_id}', {report.metadata.date_begin},
    {report.metadata.date_end}, '{errors}')
    """)

    queries.append(f"""
    INSERT INTO policy_published(
    uid, domain, adkim, aspf, p, pct, fo, rf, ri, rua, ruf, v)
    VALUES('{uid}', '{report.policy_published.domain}',
    '{report.policy_published.adkim}', '{report.policy_published.aspf}',
    '{report.policy_published.p}', '{report.policy_published.pct}',
    '{report.policy_published.fo}', '{report.policy_published.rf}',
    '{report.policy_published.ri}', '{report.policy_published.rua}',
    '{report.policy_published.ruf}', '{report.policy_published.v}')
    """)

    for r in report.records:
        queries.append(f"""
        INSERT INTO record(
        uid, source_ip, count, disposition, dkim, spf, type, comment,
        header_from, envelope_from, dkim_domain, dkim_result, dkim_hresult,
        spf_domain, spf_result)
        VALUES('{uid}', '{r.source_ip}', {r.count}, '{r.disposition}',
        '{r.dkim}', '{r.spf}', '{r.type}', '{r.comment}',
        '{r.header_from}', '{r.envelope_from}', '{r.dkim_domain}',
        '{r.dkim_result}', '{r.dkim_hresult}', '{r.spf_domain}',
        '{r.spf_result}')
        """)

    try:
        for q in queries:
            session.execute(q)

        session.commit()

    except Exception as e:
        session.rollback()
        logger.log(logger.level, e)
        raise e
