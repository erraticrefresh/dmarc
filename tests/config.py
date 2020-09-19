from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sample_dir = f'{Path(__file__).parent.absolute()}/sample'
filename = 'example.com!mail.example.com!1596254400!1596340740.xml.gz'

# https://docs.sqlalchemy.org/en/13/orm/session_basics.html#getting-a-session
# an Engine, which the Session will use for connection resources
engine = create_engine('mysql://dmarc:password@localhost/dmarc_reports')

# create a configured "Session" class
Session = sessionmaker(bind=engine)
