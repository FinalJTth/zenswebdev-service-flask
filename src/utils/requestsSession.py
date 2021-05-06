import requests
import os
from urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

class SessionWithUrlBase(requests.Session):
    # In Python 3 you could place `url_base` after `*args`, but not in Python 2.
    def __init__(self, url_base=None, verify=True, *args, **kwargs):
        super(SessionWithUrlBase, self).__init__(*args, **kwargs)
        self.url_base = url_base
        self.verify = True if os.environ.get("SSL_VERIFY") == "True" else False

    def request(self, method, url, verify=None, **kwargs):
        # Next line of code is here for example purposes only.
        # You really shouldn't just use string concatenation here,
        # take a look at urllib.parse.urljoin instead.
        verify = self.verify if verify is None else verify
        print(url[1:])
        if url[0] == '/':
            modified_url = self.url_base + url[1:]
        else:
            modified_url = self.url_base + url
        return super(SessionWithUrlBase, self).request(method, modified_url, verify=verify, **kwargs)

WSL2_ENABLE = True if os.environ.get("WSL2_ENABLE") == "True" else False
WSL2_WINDOW_HOSTNAME = os.environ.get("WSL2_WINDOW_HOSTNAME")
BACKEND_HOSTNAME = os.environ.get("BACKEND_HOSTNAME")
BACKEND_PORT = os.environ.get("BACKEND_PORT")

backend = SessionWithUrlBase(url_base=f'https://{WSL2_WINDOW_HOSTNAME if WSL2_ENABLE == True else BACKEND_HOSTNAME}:{BACKEND_PORT}/')