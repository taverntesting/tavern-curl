import logging
import json as jsonlib
import functools
import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

from future.utils import raise_from
from box import Box

from tavern.util import exceptions
from tavern.util.dict_util import check_expected_keys

logger = logging.getLogger(__name__)

# From http://pycurl.io/docs/latest/quickstart.html
def parse_header_line(header_buffer, header_line):
    # HTTP standard specifies that headers are encoded in iso-8859-1.
    # On Python 2, decoding step can be skipped.
    # On Python 3, decoding step is required.
    header_line = header_line.decode('iso-8859-1')

    # Header lines include the first status line (HTTP/1.x ...).
    # We are going to ignore all lines that don't have a colon in them.
    # This will botch headers that are split on multiple lines...
    if ':' not in header_line:
        return

    # Break the header line into header name and value.
    name, value = header_line.split(':', 1)

    # Remove whitespace that may be present.
    # Header lines include the trailing newline, and there may be whitespace
    # around the colon.
    name = name.strip()
    value = value.strip()

    # Header names are case insensitive.
    # Lowercase name here.
    name = name.lower()

    # Now we can actually record the header name and value.
    # Note: this only works when headers are not duplicated, see below.
    header_buffer[name] = value

class CurlTestSession:
    
    def __init__(self, **kwargs):

        self._curl_session = pycurl.Curl()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def make_request(self, url, verify, method, headers=None, params=None, json=None, data=None):
        
        session = self._curl_session
        # This isn't used - won't be using SSL
        if verify:
            # TODO: add SSL verify option
            pass

        session.setopt(session.URL, url)

        buffer = BytesIO()
        session.setopt(session.WRITEDATA, buffer)
        # For older PycURL versions:
        #session.setopt(session.WRITEFUNCTION, buffer.write)

        header_buffer = dict()
        header_function = functools.partial(parse_header_line, header_buffer)
        session.setopt(session.HEADERFUNCTION, header_function)

        
        if data:
            raise NotImplementedError

        if json:
            body = jsonlib.dumps(json)
            # TODO add to request

        session.perform()

        body = buffer.getvalue()
        
        response = Box({
            "code": session.getinfo(session.RESPONSE_CODE),
            "body": body,
            "headers": header_buffer,
            "timing": None,
        })

        return response
