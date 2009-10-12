#! /usr/bin/python
"""
Scan the provided directories on the command-line and report duplicate files, optionally removing them
"""
import os
import sys
import stat
import hashlib
from optparse import OptionParser
import logging
import shutil

filesBySize = {}

def walker(arg, dirname, fnames):
    d = os.getcwd()
    os.chdir(dirname)

    for f in fnames:
        if os.path.islink(f):
            continue
        if not os.path.isfile(f):
            continue
        size = os.stat(f)[stat.ST_SIZE]
        if size < 100:
            continue
        if filesBySize.has_key(size):
            a = filesBySize[size]
        else:
            a = []
            filesBySize[size] = a
        a.append(os.path.join(dirname, f))
    os.chdir(d)

parser = OptionParser(__doc__.strip())
parser.add_option("--trash",  action="store_true", default=False, help='Move duplicates to the Trash')
parser.add_option("--delete",  action="store_true", default=False, help='Delete files')
parser.add_option("--verbose", action="store_true", default=False, help="Display progress information")

(options, directories) = parser.parse_args()

if options.delete and options.trash:
    parser.error("You can delete or trash files but not both!")

logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO if options.verbose else logging.WARN
)

for x in directories:
    if not os.path.isdir(x):
        logging.error("Skipping %s: not a directory" % x)
        continue
    logging.info('Scanning "%s"' % x)
    os.path.walk(x, walker, filesBySize)

print 'Finding potential dupes...'
potentialDupes = []
potentialCount = 0
trueType = type(True)
sizes = filesBySize.keys()
sizes.sort()
for size in sizes:
    inFiles = filesBySize[size]
    outFiles = []
    hashes = {}
    if len(inFiles) == 1: continue
    logging.info('Testing %d %d byte files' % (len(inFiles), size))
    for fileName in inFiles:
        if not os.path.isfile(fileName):
            continue
        aFile = file(fileName, 'r')
        hashValue = hashlib.sha224(aFile.read(4096)).digest()
        if hashes.has_key(hashValue):
            x = hashes[hashValue]
            if type(x) is not trueType:
                outFiles.append(hashes[hashValue])
                hashes[hashValue] = True
            outFiles.append(fileName)
        else:
            hashes[hashValue] = fileName
        aFile.close()
    if len(outFiles):
        potentialDupes.append(outFiles)
        potentialCount = potentialCount + len(outFiles)
del filesBySize

logging.info('Found %d sets of potential duplicates; comparing contents for validation' % potentialCount)

dupes = []
for aSet in potentialDupes:
    outFiles = []
    hashes = {}
    for fileName in aSet:
        logging.debug('Hashing file "%s"...' % fileName)
        hashValue = hashlib.sha224(file(fileName).read()).digest()
        if hashes.has_key(hashValue):
            if not len(outFiles):
                outFiles.append(hashes[hashValue])
            outFiles.append(fileName)
        else:
            hashes[hashValue] = fileName
    if len(outFiles):
        dupes.append(outFiles)

for d in dupes:
    print 'Original:  %s' % d[0]
    
    for f in d[1:]:
        if options.delete:
            print 'Deleting:  %s' % f
            os.remove(f)
        elif options.trash:
            print 'Trashing:  %s' % f
            shutil.move(f, os.path.join(os.path.expanduser("~/.Trash/"), os.path.basename(f)))
        else:
            print "Duplicate: %s" % f
    print

        
