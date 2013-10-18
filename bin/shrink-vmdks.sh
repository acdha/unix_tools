#!/bin/sh
# Quick and dirty script to compact a large number of VMware Fusion virtualdisks

set -e

export PATH="/Applications/VMware Fusion.app/Contents/Library:$PATH"

# Note that we're using GNU Parallel solely for nicer syntax than xargs:
find -E "${1:-.}" -name \*.vmdk -a -not -iregex '^.*[-]s[0-9]+[.]vmdk$' -print0 | parallel --null 'echo {}; vmware-vdiskmanager -d {}; vmware-vdiskmanager -k {}'
