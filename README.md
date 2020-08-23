# dmarc #
[![Build Status](https://travis-ci.com/erraticrefresh/dmarc.svg?token=pnmdrqAS92wHJwmH9Sxx&branch=master)](https://travis-ci.com/erraticrefresh/dmarc)

#### INTRODUCTION ####
Parses DMARC aggregate reports and inserts the records into a database. Built with sqlalchemy.

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
doc = parser.from_file('path/to/file.xml.gz')
```
<br>

##### From bytes #####
```python
with open('path/to/file.xml.gz', 'rb') as f:
    bytes_obj = f.read()

doc = parser.from_bytes(bytes_obj)
```
<br>

##### Create a Report instance #####
```python
report = dmarc.Report(doc)
```
<br>

##### Insert report #####
Pass a session instance from sqlalchemy.
```python
report.insert(session)
```
