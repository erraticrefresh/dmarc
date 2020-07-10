from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import dmarc

#https://docs.sqlalchemy.org/en/13/orm/session_basics.html#getting-a-session
# an Engine, which the Session will use for connection
# resources
engine = create_engine('mysql://dmarc:password@localhost/dmarc_reports')

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# create Parser instance
parser = dmarc.Parser()
file = 'mockfile.com!mail.mockdomain.com!1555113601!1555200007.xml.gz'

def test_from_file():
    global parser, session
    parser.from_file(file)
    dmarc.insert_report(parser.doc, session)

def test_from_bytes():
    global parser, session

    with open(file, 'rb') as f:
        bytes_obj = f.read()

    parser.from_bytes(bytes_obj)
    dmarc.insert_report(parser.doc, session)
