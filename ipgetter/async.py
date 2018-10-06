import sys
if sys.version_info < (3, 5):
    raise NotImplementedError("Sorry, but you must be using python 3.5+ to use ipgetter.async")
import asyncio
import re
import random
import socket
from functools import partial

from ipgetter import create_opener, SERVER_LIST

@asyncio.coroutine
def myip(loop=None):
    ip = yield from AsyncIPGetter(loop).get_externalip()
    return ip

class AsyncIPGetter(object):
    """
    It should be noted, that you MUST initialize this class before using.
    """

    def __init__(self, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.get_externalip = asyncio.coroutine(self.get_externalip)
        self.fetch = asyncio.coroutine(self.fetch)
        self.test = asyncio.coroutine(self.test)

    def get_externalip(self):
        """
        This coroutine gets your IP from a random server
        """
        for server in SERVER_LIST:
            myip = yield from self.fetch(server)
            if myip and not myip.startswith("192.168"):  # For some reason, some sites return internal ip.
                return myip
        return ''

    def fetch(self, server):
        """
        This coroutine gets your IP from a specific server.
        """
        opener = create_opener()
        try:
            url = yield from self.loop.run_in_executor(None, partial(opener.open, timeout=5), server)
        except socket.timeout:
            return ''
        content = url.read()
        try:
            content = content.decode('UTF-8')
        except UnicodeDecodeError:
            content = content.decode('ISO-8859-1')

        m = re.search(
            '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
            content)
        if m:
            myip = m.group(0)
            return myip if len(myip) > 0 else ''
        return ''

    def test(self):
        '''
        This coroutine tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.
        '''


        tasks = []
        for server in SERVER_LIST:
            tasks.append(asyncio.ensure_future(self.fetch(server), loop=self.loop))
        results = yield from asyncio.gather(*tasks)

        ips = sorted(results)
        ips_set = set(ips)
        print('\nNumber of servers: {}'.format(len(SERVER_LIST)))
        print("IP's :")
        for ip, ocorrencia in zip(ips_set, map(lambda x: ips.count(x), ips_set)):
            print('{0} = {1} ocurrenc{2}'
                  .format(ip if len(ip) > 0 else 'broken server', ocorrencia, 'y' if ocorrencia == 1 else 'ies'))
        print('\n')
        print(results)

if __name__ == "__main__":
    @asyncio.coroutine
    def display_test():
        ip = yield from myip()
        print(ip)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(display_test())

