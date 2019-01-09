#!/usr/sbin/dtrace -qs
syscall::open:entry,
syscall::stat:entry,
syscall::lstat:entry,
syscall::stat64:entry,
syscall::lstat64:entry,
syscall::unlink:entry
{
	printf("%s[%d]: %s %s\n", execname, pid, probefunc, copyinstr(arg0));
}

syscall::rename:entry
{
	printf("%s[%d]: %s %s %s\n", execname, pid, probefunc, copyinstr(arg0), copyinstr(arg1));
}
