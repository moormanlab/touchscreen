import tinydb, os, requests, threading, uuid, re, psutil
import logging
import validators
import websocket
from functools import wraps
from time import sleep
from .utils import (
    protocolsPath,
    logPath,
    scan_directory,
    get_database
    )
from . import utils
from .arch import isRaspberryPI
import queue
import json

logger = logging.getLogger('BgClient')

fullProtocolsPath = os.path.abspath('protocols')

def request_handler(func):
    """wrapper for requests to handle server errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
            if not isinstance(r, requests.models.Response) or r.ok: # check if data/200 response returned
                return r 
            elif r.status_code == 401: # handle potential expired token by trying to get a new token one time.
                if func.__name__ != 'get_token': # prevent recursive loop
                    args[0].get_token()
                    r = func(*args, **kwargs)
                    if not isinstance(r, requests.models.Response) or r.ok:
                        return r
            logger.warning(f'method: {func.__name__}, status_code: {r.status_code}, detail: {r.json().get("detail")}')
            if utils.RUNNING_PROTOCOL == None:
                utils.RELOAD = True
                utils.EXIT = True
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            utils.EXIT = True
            utils.RELOAD = True

    return wrapper

def validate_url(url):
    """format url for requests library"""
    if not url.startswith(('http://', 'https://')):
        url = f'http://{url}'
    res = validators.url(url)
    assert res == True, f'Invalid url: {res}'
    return url

def get_credentials():
    """get stored credentials from touchDB.json"""
    with get_database() as db:
        device_id = db.table('settings').get(tinydb.Query().id.exists())
        device_password = db.table('settings').get(tinydb.Query().password.exists())
    return (device_id, device_password)

class BackgroundClient(threading.Thread):
    """Thread for sending/removing saved data and log files, and adding/removing protocols"""
    def __init__(self, cookies, base_url: str, creds: tuple):
        super(BackgroundClient, self).__init__()
        logger.debug('BackgroundClient created')
        self._stopevent = threading.Event()
        self.s = requests.Session()
        self.s.cookies = cookies.copy()
        self.__base_url = base_url
        self.__url = self.__base_url + '/api/devices'
        self.__id, self.__password = creds[0]['id'], creds[1]['password']

    def join(self):
        self._stopevent.set()
        super(BackgroundClient, self).join()

    def run(self):
        """main loop: polls the server for updates every 30 seconds"""
        self._stopevent.clear()


        while not self._stopevent.is_set():
            self.upload_files()
            if isRaspberryPI(): # prevent loss of protocols in dev environment 
                self.update_protocols()

            self._stopevent.wait(30)
        return



    @request_handler
    def get_token(self):
        """post to token route using session. cookie saved automatically"""
        url = self.get_url('api', 'token', base_url=True)
        payload = {'username': self.__id, 'password': self.__password, 'scope': 'device'}
        r = self.s.post(url, data=payload)
        return r

    @request_handler
    def set_status(self, status: str):
        """change status on server: depreciated"""
        url = self.get_url('status')
        payload = {'status': status}
        r = self.s.put(url, params=payload)
        return r

    @request_handler
    def download_protocol(self, content_id: str):
        """download new protocol"""
        url = self.get_url('download', content_id)
        r = self.s.get(url)
        if r.ok:
            filename = re.findall('filename="(.+)"', r.headers.get('content-disposition'))[0]
            return (filename, r.content)
        return r

    @request_handler
    def get_protocol_list(self):
        """get a list of remote protocol file names for comparison with local protocol files"""
        url = self.get_url('protocols')
        r = self.s.get(url)
        if r.ok:
            return r.json()
        return r

    @request_handler
    def upload_files(self):
        """upload safe local files and remove them from storage"""
        url = self.get_url('upload')
        filenames = self.get_local_files()
        files = [('files', open(filename, 'rb')) for filename in filenames]
        if files == []:
            return []
        r = self.s.post(url, files=files)
        if r.ok:
            for filename in filenames:
                os.remove(filename)
            return [fobj.get('filename') for fobj in r.json()]
        return r



    def get_url(self, *args, base_url: bool = False):
        """build url path from args"""
        if base_url:
            url = self.__base_url + '/'+ '/'.join(args)
        else:
            url = self.__url + '/' + '/'.join(args)
        return url

    def get_local_files(self):
        """get local data/log files without open handlers"""
        files = os.listdir(logPath)
        files = [os.path.join(logPath, file) for file in files if file.endswith(('.csv', '.log'))]
        files = [file for file in files if not self.has_handle(file)]
        return files

    def has_handle(self, file):
        """check if a file is open in some process"""
        for proc in psutil.process_iter():
            try:
                for item in proc.open_files():
                    if file == item.path:
                        return True
            except:
                pass 
        return False
    def update_protocols(self):
        """add protocols from server/remove protocols not on server"""
        local = set(scan_directory(protocolsPath))
        response = self.get_protocol_list()
        remote = {protocol.get('filename') for protocol in response}

        remove = local.difference(remote)
        create = remote.difference(local)

        for file in remove:
            f = os.path.join(fullProtocolsPath, file)
            if self.has_handle(f):
                continue
            os.remove(f)
        for file in create:
            for item in response:
                if item.get('filename') != file:
                    continue
                content_id = item.get('content_id')
                filename, content = self.download_protocol(content_id)
                filename = os.path.join(fullProtocolsPath, filename)
                with open(filename, 'wb') as fp:
                    fp.write(content)
                break

class EventClient(threading.Thread):
    """websocket thread for bi-directional communication with the server"""
    def __init__(self, cookies, q: queue.Queue, base_url: str):
        super(EventClient, self).__init__()
        logger.debug("EventClient created")
        self._stopevent = threading.Event()
        self.__cookies = f'Authorization={cookies.get("Authorization")}'
        self.q = q
        self.__base_url = base_url
        self.__url = self.__base_url + '/api/devices/stream'
        self.__url = f'ws://{self.__url.split("://", 1)[1]}'
        self.client = websocket.WebSocket()

    def join(self):
        self._stopevent.set()
        try:
            self.client.close()
        except websocket.WebSocketException as e:
            logger.exception(e)
        super(EventClient, self).join()

    def run(self):
        """main loop: recieve/send messages"""
        self._stopevent.clear()
        try:
            self.client.connect(self.__url, cookie=self.__cookies)
        except websocket.WebSocketException as e:
            logger.exception(e)
            utils.EXIT = True
            utils.RELOAD = True
        try:
            for msg in self.client:
                if self._stopevent.is_set():
                    break
                self.handle_event(msg)
        except websocket.WebSocketException as e:
            logger.exception(e)
            utils.EXIT = True
            utils.RELOAD = True


    def handle_event(self, msg):
        """handle or delegate the event recieved from server"""
        data = json.loads(msg)
        if data.get('event') == 'stop':
            if getattr(utils.RUNNING_PROTOCOL, 'quit', None) != None:
                utils.RUNNING_PROTOCOL.quit()
        else:
            self.q.put(data)
 
    

class ClientManager:
    """mangage clients"""
    def __init__(self, q):
        self.q = q
        self.__cookies = None
        with get_database() as db:
            self.__base_url = db.table('settings').get(tinydb.Query().server.exists())['server']
        self.__base_url = validate_url(self.__base_url)

        if get_credentials()[0]['id'] == 'None':
            self.register()
        self.get_token()
        self.early_exit = not self.safe_connect()
        if not self.early_exit:
            creds = get_credentials()
            self.background_client = BackgroundClient(self.__cookies.copy(), self.__base_url, creds)
            self.event_client = EventClient(self.__cookies.copy(), self.q, self.__base_url)

    def start(self):
        if self.early_exit:
            return True

        self.background_client.start()
        self.event_client.start()
        logger.info('Background Threads Started')
        return False

    def join(self):
        self.q.join()
        if not self.early_exit:
            self.event_client.join()
            self.background_client.join()
            logger.info('Background Threads Joined')

    def safe_connect(self):
        """check if device is verified and can connect without issue"""
        url = self.get_url('api', 'devices', 'whoami')
        try:
            r = requests.get(url, cookies=self.__cookies)
            return r.ok
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            return False
    def get_token(self):
        """try to get token as cookie"""
        url = self.get_url('api', 'token')
        creds = get_credentials()
        payload = {'username': creds[0]['id'], 'password': creds[1]['password'], 'scope': 'device'}
        try:
            r = requests.post(url, data=payload)
            if r.ok:
                self.__cookies = r.cookies.copy()
        except requests.exceptions.RequestException as e:
            logger.exception(e)

    def sync_status(self, status, retries=1):
        url = self.get_url('api', 'devices', 'status')
        payload = {'status': status}
        try:
            r = requests.put(url, params=payload, cookies=self.__cookies)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
        else:
            if r.ok:
                return
            elif retries > 0:
                self.get_token()
                self.sync_status(status=status, retries=retries - 1)
            else:
                logger.error(f'could not set remote status to: {status}, message: {r.json().get("detail")}')

    
    def register(self):
        """try to register/save credentials"""
        url = self.get_url('api', 'devices', 'register')
        payload = {'name': str(uuid.uuid4()), 'password': get_credentials()[1]['password']}
        try:
            r = requests.post(url, json=payload)
            if r.ok:
                dev_id = r.json().get('id')
                with get_database() as db:
                    db.table('settings').update({'id': dev_id}, doc_ids=[get_credentials()[0].doc_id])
        except requests.exceptions.RequestException as e:
            logger.exception(e)
    def get_url(self, *args):
        """build url path from args"""
        url = self.__base_url + '/'+ '/'.join(args)
        return url
