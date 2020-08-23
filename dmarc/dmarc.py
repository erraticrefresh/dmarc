from xml.etree import ElementTree as ET
from gzip import decompress, BadGzipFile
from uuid import uuid4
from pathlib import Path
from datetime import datetime
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
    """
    DMARC Parser class

    Attributes:
        tolerance (str): xml schema leniency
        schema (obj): XMLSchema instance
    """
    def __init__(self, tolerance='minimal'):
        """
        Arguments:
            tolerance (str): xml schema leniency
        """
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
        Validate xml report elements. Accepts XML bytes or .xml or .xml.gz
        filepath

        Arguments:
            src (bytes or str): filepath or file bytes
        """
        try:
            return self.schema.is_valid(src.decode())

        except AttributeError:
            if src.endswith('.gz'):
                with open(src, 'rb') as f:
                    return self.schema.is_valid(
                        decompress(f.read()).decode())

            return self.schema.is_valid(src)

        except Exception as e:
            logger.log(logger.level, [e, src])

class Report:
    """
    DMARC Report class
    Extract the DMARC metadata as defined here:
    https://tools.ietf.org/html/rfc7489 in Appendix C
    If no data is found, return NA
    """
    def __init__(self, doc):
        """
        Arguments:
            doc (obj): ElementTree instance
        """
        self.version = doc.findtext('version')
        self.metadata = {
            'org_name': doc.findtext('report_metadata/org_name', default='NA'),
            'email': doc.findtext('report_metadata/email', default='NA'),
            'extra_contact_info': doc.findtext(
                'report_metadata/extra_contact_info', default='NA'),

            'report_id': doc.findtext(
                'report_metadata/report_id', default='NA'),

            'date_begin': datetime.utcfromtimestamp(int(
                doc.findtext('report_metadata/date_range/begin'))),

            'date_end': datetime.utcfromtimestamp(int(
                doc.findtext('report_metadata/date_range/end'))),

            'errors': [e for e in doc.findall('report_metadata/error')]
        }

        self.policy_published = {
            'domain': doc.findtext('policy_published/domain', default='NA'),
            'adkim': doc.findtext('policy_published/adkim', default='NA'),
            'aspf': doc.findtext('policy_published/aspf', default='NA'),
            'p': doc.findtext('policy_published/p', default='NA'),
            'pct': doc.findtext('policy_published/pct', default='NA'),
            'fo': doc.findtext('policy_published/fo', default='NA'),
            'rf': doc.findtext('policy_published/rf', default='NA'),
            'ri': doc.findtext('policy_published/ri', default='NA'),
            'rua': doc.findtext('policy_published/rua', default='NA'),
            'ruf': doc.findtext('policy_published/ruf', default='NA'),
            'v': doc.findtext('policy_published/v', default='NA')
        }

        self.records = [{
            'source_ip':  rec.findtext('row/source_ip', default='NA'),
            'count': int(rec.findtext('row/count', default='NA')),
            'disposition': rec.findtext(
                'row/policy_evaluated/disposition', default='NA'),

            'dkim': rec.findtext('row/policy_evaluated/dkim', default='NA'),
            'spf': rec.findtext('row/policy_evaluated/spf', default='NA'),
            'type': rec.findtext(
                'row/policy_evaluated/reason/type', default='NA'),

            'comment': rec.findtext(
                'row/policy_evaluated/reason/comment', default='NA'),

            'header_from': rec.findtext(
                'identifiers/header_from', default='NA'),

            'envelope_from': rec.findtext(
               'identifiers/envelope_from', default='NA'),

            'dkim_domain': rec.findtext(
                'auth_results/dkim/domain', default='NA'),

            'dkim_result': rec.findtext(
                'auth_results/dkim/result', default='NA'),

            'dkim_hresult': rec.findtext(
                'auth_results/dkim/human_result', default='NA'),

            'spf_domain': rec.findtext('auth_results/spf/domain', default='NA'),
            'spf_result': rec.findtext('auth_results/spf/result', default='NA')

        } for rec in doc.findall('record')]

    def insert(self, session):
        """
        Insert DMARC Aggregate Report into database

        Arguments:
            report (obj): Report instance
            session (obj): SQLAlchemy session instance
        """
        uid = uuid4()
        errors = " | ".join(self.metadata['errors']) \
            if self.metadata['errors'] else "NA"

        queries = []

        queries.append(f"""
        INSERT INTO report_metadata(
        uid, organization, email, extra_contact_info,
        report_id, date_begin, date_end, `errors`)
        VALUES(
            '{uid}',
            '{self.metadata['org_name']}',
            '{self.metadata['email']}',
            '{self.metadata['extra_contact_info']}',
            '{self.metadata['report_id']}',
            '{self.metadata['date_begin'].strftime('%Y-%m-%d %H:%M:%S')}',
            '{self.metadata['date_end'].strftime('%Y-%m-%d %H:%M:%S')}',
            '{errors}')
        """)

        queries.append(f"""
        INSERT INTO policy_published(
        uid, domain, adkim, aspf, p, pct, fo, rf, ri, rua, ruf, v)
        VALUES(
            '{uid}',
            '{self.policy_published['domain']}',
            '{self.policy_published['adkim']}',
            '{self.policy_published['aspf']}',
            '{self.policy_published['p']}',
            '{self.policy_published['pct']}',
            '{self.policy_published['fo']}',
            '{self.policy_published['rf']}',
            '{self.policy_published['ri']}',
            '{self.policy_published['rua']}',
            '{self.policy_published['ruf']}',
            '{self.policy_published['v']}')
        """)

        for r in self.records:
            queries.append(f"""
            INSERT INTO record(
            uid, source_ip, count, disposition, dkim, spf, type, comment,
            header_from, envelope_from, dkim_domain, dkim_result, dkim_hresult,
            spf_domain, spf_result)
            VALUES(
                '{uid}',
                '{r['source_ip']}',
                {r['count']},
                '{r['disposition']}',
                '{r['dkim']}',
                '{r['spf']}',
                '{r['type']}',
                '{r['comment']}',
                '{r['header_from']}',
                '{r['envelope_from']}',
                '{r['dkim_domain']}',
                '{r['dkim_result']}',
                '{r['dkim_hresult']}',
                '{r['spf_domain']}',
                '{r['spf_result']}')
            """)

        try:
            for q in queries:
                session.execute(q)

            session.commit()

        except Exception as e:
            session.rollback()
            logger.log(logger.level, e)
            raise e
