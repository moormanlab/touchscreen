import csv
import functools
import datetime
import os
import inspect


class CSVLogger:
    def __init__(self, protocol: str, subject=None, experimenter=None):
        self._start = datetime.datetime.now()
        self.__set_filename(protocol, subject, experimenter)
        self._header = ['datetime', 'runtime', 'method', 'event', 'x-cord', 'y-cord']
        self.__csvfile = open(self.filename, 'w', newline='')
        self.__is_active = False


    def configure(self, header=None, replace=False):
        if header != None:
            if replace:
                self._header = header
            else:
                self._header += header

    def start(self):
        self.__writer = csv.DictWriter(self.__csvfile, fieldnames=self._header, extrasaction='ignore')
        self.__writer.writeheader()
        self.__is_active = True

    def is_active(self):
        return self.__is_active

    def log(self, method=None, event=None, **kwargs):
        if event is not None and not 'event' in self._header and kwargs == {}: # quick fix. will remove soon
            return
        fields = {'datetime': datetime.datetime.now().strftime('%H:%M:%S.%f'), 'runtime': self.time_delta()}
        if event.__class__.__name__ == 'tsEvent': # bad practice but don't want to deal with circular import errors
            fields.update({'event': event.get_type(), 'x-cord': event.position[0], 'y-cord': event.position[1]})
        elif event != None:
            fields.update({'event': event})
        if method != None:
            fields.update({'method': method})
        else:
            fields.update({'method': inspect.currentframe().f_back.f_code.co_name})
        fields.update(kwargs)
        self.__writer.writerow(fields)

    def time_delta(self):
        diff = datetime.datetime.now() - self._start
        return diff.total_seconds()

    def __set_filename(self, protocol, subject, experimenter):
        logPath = os.path.abspath('logs')
        file_name = protocol+'_'+subject+'_'+experimenter+'_'+self._start.strftime('%-m_%-d-%H_%M')+'.csv'
        self.filename = os.path.join(logPath, file_name)
