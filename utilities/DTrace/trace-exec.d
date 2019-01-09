#!/usr/sbin/dtrace -s
syscall::execve:entry
{
	trace(pid);
	trace(execname);
	trace(copyinstr(arg0));
}
