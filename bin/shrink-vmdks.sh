#!/bin/sh
# Quick and dirty script to compact a large number of VMware Fusion virtualdisks

set -e

export PATH="/Applications/VMware Fusion.app/Contents/Library:$PATH"

# Note that we're using GNU Parallel solely for nicer syntax than xargs:
find "${1:-.}" -name \*.vmdk -print0 | grep -z -v -E "[-]s[0-9]+[.]vmdk" | parallel --null --ungroup -j 1 'echo {}; vmware-vdiskmanager -d {}; vmware-vdiskmanager -k {}'
