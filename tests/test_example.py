from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import dmarc

sample_dir = f'{Path(__file__).parent.absolute()}/sample'
file = f'{sample_dir}/example.com!mail.example.com!1555113601!1555200007.xml.gz'

# https://docs.sqlalchemy.org/en/13/orm/session_basics.html#getting-a-session
# an Engine, which the Session will use for connection
# resources
engine = create_engine('mysql://dmarc:password@localhost/dmarc_reports')

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# create a Parser
parser = dmarc.Parser()

def test_from_file():

    doc = parser.from_file(file)
    report = dmarc.Report(doc)
    dmarc.insert_report(report, session)

def test_from_bytes():

    with open(file, 'rb') as f:
        bytes_obj = f.read()

    doc = parser.from_bytes(bytes_obj)
    report = dmarc.Report(doc)
    dmarc.insert_report(report, session)
