#!/usr/sbin/dtrace -s

#pragma D option quiet

fbt::lockd_request:entry
{
	self->timestamp = timestamp;
	self->pid = pid;
	self->execname = execname;
	printf("%s[%d] entry %Y\n", execname, pid, walltimestamp);
} 

fbt::lockd_request:return
{
	printf("%s[%d] return %Y (elapsed = %d)\n", self->execname, self->pid, walltimestamp, (timestamp - self->timestamp)  / 1000000000 );
} 
