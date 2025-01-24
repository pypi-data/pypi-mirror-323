""" Module for scanning and extracting data from aplog-generated files.
"""
import sys, time, argparse, os
from timeit import default_timer as timer
#from pprint import pprint
import bisect
import numpy as np
from io import BytesIO
import msgpack
import msgpack_numpy
msgpack_numpy.patch()
__version__ = 'v1.4.1 2021-07-30'#
#TODO: the par2key is mapped to int now, therefore both par2key and key2par could be just lists, that could be faster.

#````````````````````````````Globals``````````````````````````````````````````
Nano = 0.000000001
TimeFormat_in = '%y%m%d_%H%M%S'
TimeFormat_out = '%y%m%d_%H%M%S'
MaxFileSize = 4*1024*1024*1024
#````````````````````````````Helper functions`````````````````````````````````
def _printv(msg):
    if APScan.Verbosity >= 1:
        print(f'DBG_APSV: {msg}')
def _printvv(msg):
    if APScan.Verbosity >= 2 :
        print(f'DBG_APSVV: {msg}')

def _timeInterval(startTime, span):
    """returns sections (string) and times (float) of time interval
    boundaries"""
    ttuple = time.strptime(startTime,TimeFormat_in)
    startSection = time.strftime(TimeFormat_out, ttuple)
    startTime = time.mktime(ttuple)
    endTime = startTime +span
    endTime = min(endTime, 4102462799.)# 2099-12-31
    ttuple = time.localtime(endTime)
    endSection = time.strftime(TimeFormat_out, ttuple)
    _printv(f'start,end:{startSection, endSection}')
    return startSection, startTime, endSection, endTime
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#````````````````````````````class APView`````````````````````````````````````
class APScan():
    Verbosity = 0
    """Show dedugging messages."""

    def __init__(self, fileName):
        """Open logbook fileName, unpack headers, position file to data sections."""
        self.logbookName = fileName
        try:
            self.logbookSize = os.path.getsize(fileName)
        except Exception as e:
            print(f'ERROR opening file {fileName}: {e}')
            sys.exit()
        self.logbook = open(fileName,'rb')
        if self.logbookSize < MaxFileSize:
            ts = timer()
            rbuf = self.logbook.read()
            ts1 = timer()
            dt1 = round(ts1 - ts,6)
            self.logbook = BytesIO(rbuf)
            dt2 = round(timer() - ts1,6)
            _printv(f'read time: {dt1}, adopted in {dt2}')
        else:
            print(f'File size > {self.logbookSize}, processing it sequentially')

        # unpack logbook contents and set file position after it
        self.unpacker = msgpack.Unpacker(self.logbook, use_list=False
        ,strict_map_key=False) #use_list speeds up 20%, # does not help:, read_size=100*1024*1024)
        self.dirSize = 0
        self.directory = []
        for contents in self.unpacker:
            #printvv(f'Table of contents: {contents}')
            try:
                self.dirSize = contents['contents']['size']
            except:
                print('Warning: Table of contents is missing or wrong')
                break
            self.directory = contents['data']
            break

        # unpack two sections after the contents: Abstract and Index
        self.position = self.dirSize
        self.logbook.seek(self.position)
        self.unpacker = msgpack.Unpacker(self.logbook, use_list=False
        ,strict_map_key=False) #use_list speeds up 20%, # does not help:, read_size=100*1024*1024)
        nSections = 0
        for section in self.unpacker:
            #print(f'section:{nSections}')
            nSections += 1
            if nSections == 1:# section: Abstract
                _printvv(f'Abstract@{self.logbook.tell()}: {section}')
                self.abstract = section['abstract']
                self.compression = self.abstract.get('compression')
                if self.compression is None:
                    continue
                if self.compression != 'None':
                    module = __import__(self.compression)
                    self.decompress = module.decompress
                continue
            if nSections == 2:# section: Index
                self.par2key = section['index']
                self.key2par = {value[0]:key for key,value in self.par2key.items()}
                _printvv(f'Index@{self.logbook.tell()}: {self.key2par}')                
                break

    def get_headers(self):
        """Returns dict of header sections: Directory, Abstract, Index"""
        return {'Directory':self.directory, 'Abstract':self.abstract
        , 'Index':self.key2par}

    def extract_objects(self, span=0., items=[], startTime=None):
        """
        Returns correlated dict of times and values of the logged items during
        the selected time interval.
        
        **span**:   Time interval for data extraction in seconds. If 0, then the
                data will be extracted starting from the startTime and ending 
                at the end of the logbook.
        
        **items**:  List of items to extract. Item are coded with keys. 
                The mapping of the Process Variables (PV) could be found in
                the self.par2key map. The reversed mapping is in the 
                self.key2par map.
        
        **startTime**: String for selecting start of the extraction interval. 
                Format: YYMMDD_HHMMSS. Set it to None for the logbook beginning. 
                """
        extracted = {}
        parameterStatistics = {}

        if len(items) == 0: # enable handling of all items 
            items = self.key2par.keys()
        for key,par in self.key2par.items():
            if par not in parameterStatistics:
                #print(f'add to stat[{len(parameterStatistics)+1}]: {par}') 
                parameterStatistics[key] = 0
            if par not in extracted and key in items:
                    _printvv(f'add extracted[{len(extracted)+1}]: {par}') 
                    extracted[key] = {'par':par, 'time':[], 'value':[]}
        
        if startTime is not None:
            startSection, startTStamp, endSection, endTime\
            = _timeInterval(startTime, span)

        # re-create the unpacker for reading logbook starting from required section
        if len(self.directory) != 0 and startTime:
            keys = list(self.directory.keys())
            nearest_idx = bisect.bisect_left(keys, startSection)
            if keys[nearest_idx] != startSection:
                startSection = keys[nearest_idx-1]
            _printvv(f'start section {startSection, startTStamp, endTime}')
            self.position = self.directory[startSection]
            self.logbook.seek(self.position)
            _printvv(f'logbook positioned to section {startSection}, offset={self.dirSize}')
            self.unpacker = msgpack.Unpacker(self.logbook, use_list=False
            ,strict_map_key=False) #use_list speeds up 20%, # does not help:, read_size=100*1024*1024)

        # loop over sections in the logbook
        tstart = time.time()
        nSections = 0
        nParagraphs = 0
        reached_endTime = False
        if APScan.Verbosity >= 1:
        	sectionTime = [0.]*3
        for section in self.unpacker:
            if reached_endTime:
                break
            nSections += 1
            # data sections
            #print(f'Data Section: {nSections}')
            dt = time.time() - tstart
            if nSections%60 == 0:
                _printv((f'Data sections: {nSections}, paragraphs: {nParagraphs}'
                f', elapsed time: {round(dt,4)}, paragraphs/s: {nParagraphs//dt}'))
            try:
                if self.compression != 'None':
                    ts = timer()
                    decompressed = self.decompress(section)
                    if APScan.Verbosity >= 1:
                    	sectionTime[0] += timer() - ts
                    ts = timer()
                    section = msgpack.unpackb(decompressed
                    ,strict_map_key=False)
                    if APScan.Verbosity >= 1:
                    	sectionTime[1] += timer() - ts
                sectionDatetime, paragraphs = section
            except Exception as e:
                print(f'WARNING: wrong section {nSections}: {str(section)[:75]}...', {e})
                break
            if startTime is None:
                startSection, startTStamp, endSection, endTime\
                = _timeInterval(sectionDatetime, span)
                startTime = startTStamp
                
            if sectionDatetime > endSection:
                _printvv(f'reached last section {sectionDatetime}')
            nParagraphs += len(paragraphs)

            # iterate paragraphs
            ts = timer()
            try:
                for timestamp,parkeys in paragraphs:
                    timestamp *= Nano
                    #print(f'paragraph: {timestamp}')#, parkeys}')
                    if timestamp < startTStamp:
                        continue
                    if timestamp > endTime:
                        _printvv(f'reached endTime {endTime}')
                        reached_endTime =True
                        break
                    for key in parkeys:
                        if key not in items:
                            continue
                        parameterStatistics[key] += 1
                        values = parkeys[key]
                        try:    nVals = len(values)
                        except: values = [values] # make it subscriptable
                        extracted[key]['time'].append(timestamp)
                        extracted[key]['value'].append(values)
            except Exception as e:
                print(f'WARNING: wrong paragraph {nParagraphs}: {e}')

            if APScan.Verbosity >= 1:
            	sectionTime[2] += timer() - ts
        if APScan.Verbosity >= 1:
        	print(f'SectionTime: {[round(i/nSections,6) for i in sectionTime]}')
        print(f'Deserialized from {self.logbookName}: {nSections} sections, {nParagraphs} paragraphs')
        print(f'Sets/Parameter: {parameterStatistics}')
        dt = time.time() - tstart
        mbps = f', {round((self.logbook.tell() - self.position)/1e6/dt,1)} MB/s'
        print((f'Elapsed time: {round(dt,4)} s, {int(nParagraphs/dt)}'
        f' paragraphs/s')+mbps)
        return extracted
