"""Test of an upstrim-generated file: deserialze and plotItem all its items"""
import sys, time, argparse
from timeit import default_timer as timer
from functools import partial
import numpy as np
import msgpack
import msgpack_numpy
msgpack_numpy.patch()
import pyqtgraph as pg

__version__ = 'v06 2021-06-14'# improved plotting: cursors, legends.

#````````````````````````````Helper methods```````````````````````````````````
def decompress(arg):
    # Stub function for decompressing
    return
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#````````````````````````````Deserialize files````````````````````````````````
parser = argparse.ArgumentParser(description=__doc__)
#parser.add_argument('-k', '--keys', help=('Items to plot. '
#'String of 1-letter keys of the parameter map e.g. 1357'))
parser.add_argument('-f', '--fastPlotting', action='store_true', help=\
'Fast plotting (for large data sets)')
parser.add_argument('files', nargs='*', default='apstrim.aps', help=\
'Input files, Unix style pathname pattern expansion allowed e.g: pi0_2021*.aps')
pargs = parser.parse_args()
#print(f'pargs: {pargs}')
print(f'files: {pargs.files}')

plotData ={}
for file in pargs.files:
    print(f'Processing {file}')
    f = open(file,'rb')
    book = msgpack.Unpacker(f)
    
    nSections = 0
    nParagraphs = 0
    for section in book:
        #if nSections > 100:  break
        nSections += 1
        if nSections == 1:# skip info section 
            print(f'file info: {section}')
            compression = section.get('compression')
            if compression is None:
                continue
            if compression != 'None':
                module = __import__(compression)
                decompress = module.decompress
            continue
        if nSections == 2:# section: parameters
            par2key = section['parameters']
            key2par = {value[0]:key for key,value in par2key.items()}
            print(f'parameter map: {key2par}')
            for key,par in key2par.items():
                #if key not in plotData:
                #    plotData[key] = {'par':par, 'x':[], 'y':[]}
                if par not in plotData:
                    #print(f'add to graph[{len(plotData)+1}]: {par}') 
                    plotData[par] = {'x':[], 'y':[]}
            continue
    
        # data sections
        #print(f'dsec: {section}')
        try:
            if compression != 'None':
                decompressed = decompress(section)
                section = msgpack.unpackb(decompressed)
            sectionDatetime, paragraphs = section
        except Exception as e:
            print(f'WARNING: wrong section {nSections}: {str(section)[:75]}...')
            continue
        nParagraphs += len(paragraphs)
        try:
          for timestamp,parkeys in paragraphs:
            #print(f'paragraph: {timestamp,parkeys}')
            for key,value in parkeys.items():
                par = key2par[key]
                # if value is a vector then append all its points spaced by 1 us
                for i,v in enumerate(value):
                    plotData[par]['x'].append(timestamp + i*1.e-6)
                    plotData[par]['y'].append(v)
                    #print(f'key {key}, ts: {timestamp}')
        except Exception as e:
            print(f'WARNING: wrong paragraph {nParagraphs}')

    print(f'Deserialized from {file}: {nSections} sections, {nParagraphs} paragraphs')
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,    
#```````````````````````````` Plot objects````````````````````````````````````
class DateAxis(pg.AxisItem):
    """Time scale for plotItem"""
    def tickStrings(self, values, scale, spacing):
        strns = []
        if len(values) == 0: 
            return ''
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%d %H:%M:%S'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
        elif rng >=3600*24*30*24:
            string = '%Y'
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns


#QT5#win = pg.GraphicsLayoutWidget(show=True)#, title="Basic plotting examples")
qApp = pg.mkQApp()
win = pg.GraphicsLayoutWidget()
win.show()

win.resize(800,600)
s = pargs.files[0] if len(pargs.files)==1 else pargs.files[0]+'...'
win.setWindowTitle(f'Graphs[{len(plotData)}] of {s}')

plotItem = win.addPlot(#title="apstrim plotItem",
    axisItems={'bottom':DateAxis(orientation='bottom')})
legend = pg.LegendItem((80,60), offset=(70,20))
legend.setParentItem(plotItem)
viewBox = plotItem.getViewBox()
viewBox.setMouseMode(pg.ViewBox.RectMode)

idx = 0
ts = timer()
nPoints = 0
viewRect = plotItem.viewRect()
xSize = int(viewRect.right() - viewRect.left())
for par,xy in plotData.items():
    print(f'Graph[{idx}]: {par}')
    idx += 1
    # sort points along X
    a = np.stack([xy['x'],xy['y']])
    a = a[:, a[0, :].argsort()]
    pen = (idx,len(plotData))
    npt = len(a[0])
    nPoints += npt
    try:
        if pargs.fastPlotting or npt/xSize > 100:
            # plotting of only lines
            p = plotItem.plot(a[0], a[1], pen=pen)
        else:
            # plotting with symbols is 10 times slower
            p = plotItem.plot(a[0], a[1], pen=pen
            ,symbol='+', symbolSize=2, symbolPen=pen)
        legend.addItem(p, par)
    except Exception as e:
        print(f'WARNING: plotting is not supported for item {par}: {e}')
print(f'plotting time of {nPoints} points: {round(timer()-ts,3)} s')

cursors = set()
def add_cursor(direction):
    global cursor
    angle = {'Vertical':90, 'Horizontal':0}[direction]
    vid = {'Vertical':0, 'Horizontal':1}[direction]
    viewRange = plotItem.viewRange()
    pos = (viewRange[vid][1] + viewRange[vid][0])/2.
    pen = pg.mkPen(color='y', width=1, style=pg.QtCore.Qt.DotLine)
    cursor = pg.InfiniteLine(pos=pos, pen=pen, movable=True, angle=angle
    , label=str(round(pos,3)))
    cursor.sigPositionChangeFinished.connect(\
    (partial(cursorPositionChanged,cursor)))
    cursors.add(cursor)
    plotItem.addItem(cursor)
    cursorPositionChanged(cursor)

def cursorPositionChanged(cursor):
    pos = cursor.value()
    horizontal = cursor.angle == 0.
    viewRange = plotItem.viewRange()[horizontal]
    if pos > viewRange[1]:
        plotItem.removeItem(cursor)
        cursors.remove(cursor)
    else:
        if horizontal:
            text = str(round(pos,3))
        else:
            text = time.strftime('%H:%M:%S', time.localtime(pos))
        cursor.label.setText(text)

add_cursor('Vertical')
add_cursor('Horizontal')

qApp.exec_()
