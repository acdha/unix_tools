#!/usr/sbin/dtrace -s

syscall::nfs*:entry
/execname == "rpc.lockd"/
{
	trace(pid);
	trace(probefunc);
}
