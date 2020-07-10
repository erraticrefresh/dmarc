# dmarc #
[![Build Status](https://travis-ci.com/erraticrefresh/dmarc.svg?branch=master)](https://travis-ci.com/erraticrefresh/dmarc)

#### INTRODUCTION ####
dmarc is a module for Python that parses DMARC aggregate reports and inserts the records into a database. Built with sqlalchemy.

### Usage ###
<hr>

##### Parser #####

```python
import dmarc

parser = dmarc.Parser()
```
<br>

##### From file #####
```python
parser.from_file('path/to/file.xml.gz')
```
<br>

##### From bytes #####
```python
with open('path/to/file.xml.gz', 'rb') as f:
    bytes_obj = f.read()

parser.from_bytes(bytes_obj)
```
<br>

##### Insert records #####
Pass a session instance from sqlalchemy.
```python
dmarc.insert_report(parser.doc, session)
```
