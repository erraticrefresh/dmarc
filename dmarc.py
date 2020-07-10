
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from gzip import GzipFile, BadGzipFile, decompress
import logging

logger = logging.getLogger()

class Parser:
    """
    DMARC report parser

    Attributes:
        fp (str): file path
        doc (obj): ElementTree class instance
    """
    def from_file(self, fp):
        """
        Parse XML from .gz or .xml
        Arguments:
            fp (str): file path
        """
        try:
            # from .gz
            dom = ET.parse(GzipFile(fp))
            self.doc = dom.getroot()

        except BadGzipFile:
            # if not .gz, .xml
            dom = ET.parse(fp), ET.XMLParser(encoding='utf-8')
            self.doc = dom.getroot()

        except Exception as e:
            logger.log(logger.level, [e, fp])
            raise e

    def from_bytes(self, data):
        """
        Parse XML from bytes file data

        Arguments:
            data(bytes): bytes file object
        """

        # from .gz bytes
        try:
            self.doc = ET.fromstring(decompress(data))

        # if not .gz, .xml bytes
        except BadGzipFile:
            self.doc = ET.fromstring(data)

        except Exception as e:
            logger.log(logger.level, e)
            raise e

def insert_report_metadata(uid, doc, session):
    """
    Extract the DMARC metadata as defined here:
    http://www.dmarc.org/draft-dmarc-base-00-02.txt in Appendix C
    If no data is found, return NA

    Arguments:
        uid (obj): unique id for report data primary key
        doc (obj): ElementTree class instance
        session (obj): SQLAlchemy session instance
    """
    org_name = doc.findtext(
        'report_metadata/org_name', default='NA')

    email = doc.findtext(
        'report_metadata/email', default='NA')

    extra_contact_info = doc.findtext(
        'report_metadata/extra_contact_info', default='NA')

    report_id = doc.findtext(
        'report_metadata/report_id', default='NA')

    date_range_begin = doc.findtext(
        'report_metadata/date_range/begin', default='NA')
    date_range_begin = int(date_range_begin) \
        if date_range_begin != 'NA' else 'NA'

    date_range_end = doc.findtext(
        'report_metadata/date_range/end', default='NA')
    date_range_end = int(date_range_end) \
        if date_range_end != 'NA' else 'NA'

    sql = (
        f"INSERT INTO report_metadata("
        "uid, organization, email, extra_contact_info, "
        "report_id, date_begin, date_end) "
        f"VALUES('{uid}', '{org_name}', '{email}', '{extra_contact_info}', "
        f"'{report_id}', {date_range_begin}, {date_range_end})")

    session.execute(sql)

def insert_policy_published(uid, doc, session):
    """
    Extract the DMARC policy published information as defined here:
    http://www.dmarc.org/draft-dmarc-base-00-02.txt in Section 6.2
    If no data is found, return NA

    Arguments:
        uid (obj): unique id for report data primary key
        doc (obj): ElementTree class instance
        session (obj): SQL session instance
    """
    domain = doc.findtext('policy_published/domain', default='NA')
    adkim = doc.findtext('policy_published/adkim', default='NA')
    aspf = doc.findtext('policy_published/aspf', default='NA')
    p = doc.findtext('policy_published/p', default='NA')
    pct = doc.findtext('policy_published/pct', default=0)
    pct = int(pct) if pct != 0 else 0

    sql = (f"INSERT INTO policy_published("
        "uid, domain, adkim, aspf, p, pct) "
        f"VALUES('{uid}', '{domain}', '{adkim}', '{aspf}', '{p}', {pct})")

    session.execute(sql)

def insert_records(uid, doc, session):
    """
    Extract the DMARC records as defined here:
    http://www.dmarc.org/draft-dmarc-base-00-02.txt in Appendix C
    If no data is found, return NA

    Arguments:
        uid (obj): unique id for report data primary key
        doc (obj): ElementTree class instance
        session (obj): SQLAlchemy session instance
    """
    container = doc.findall('record')
    for elem in container:
        source_ip = elem.findtext('row/source_ip', default='NA')

        count = elem.findtext('row/count', default=0)
        count = int(count) if count != 0 else 0

        ft = elem.findtext
        disposition = ft('row/policy_evaluated/disposition', default='NA')
        dkim = ft('row/policy_evaluated/dkim', default='NA')
        spf = ft('row/policy_evaluated/spf', default='NA')
        _type = ft('row/policy_evaluated/reason/type', default='NA')
        comment = ft('row/policy_evaluated/reason/comment', default='NA')
        header_from = ft('identifiers/header_from', default='NA')
        dkim_domain = ft('auth_results/dkim/domain', default='NA')
        dkim_result = ft('auth_results/dkim/result', default='NA')
        dkim_hresult = ft('auth_results/dkim/human_result', default='NA')
        spf_domain = ft('auth_results/spf/domain', default='NA')
        spf_result = ft('auth_results/spf/result', default='NA')

        sql = (f"INSERT INTO record("
            "uid, source_ip, count, disposition, dkim, spf, _type, "
            "comment, header_from, dkim_domain, dkim_result, dkim_hresult, "
            "spf_domain, spf_result) "
            f"VALUES('{uid}', '{source_ip}', {count}, '{disposition}', "
            f"'{dkim}', '{spf}', '{_type}', '{comment}', '{header_from}', "
            f"'{dkim_domain}', '{dkim_result}', '{dkim_hresult}', "
            f"'{spf_domain}', '{spf_result}')")

        session.execute(sql)

def insert_report(doc, session):
    """
    Insert DMARC Aggregate Report into database

    Arguments:
        doc (obj): ElementTree class instance
        session (obj): SQLAlchemy session instance
    """
    uid = uuid4()
    try:
        insert_report_metadata(uid, doc, session)
        insert_policy_published(uid, doc, session)
        insert_records(uid, doc, session)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.log(logger.level, e)
        raise e
