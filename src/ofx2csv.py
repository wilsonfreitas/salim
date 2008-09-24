#!/usr/bin/env python

import sys
import csv      
import codecs         
import cStringIO
from ofx import OFXParser

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("usage: ofx2csv <ofxfile.ofx> <output.csv> \n\n")
        sys.exit(1)

    ofxfilename, csvfilename = sys.argv[1:3]
    
    parser = OFXParser(ofxfilename)
    bankid = parser['bankacctfrom']['bankid']
    acctid = parser['bankacctfrom']['acctid']
    
    rows = []
    for trans in parser['stmttrn']:
        r = []
        r.append(trans['dtposted'])
        r.append(trans['trnamt'])
        r.append(trans['memo'])
        r.append(trans['checknum'])
        r.append(trans['fitid'])
        r.append(bankid)
        r.append(acctid)
        
        rows.append(tuple(r))

    csv_file = file(csvfilename, 'wb')
    csv_writer = UnicodeWriter(csv_file)
    csv_writer.writerows(rows)
    csv_file.close()
    
if __name__ == '__main__':
    main()
