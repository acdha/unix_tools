#!/usr/sbin/dtrace -s
fbt::nfs*:entry
{
   trace(pid);
   trace(execname);
}
