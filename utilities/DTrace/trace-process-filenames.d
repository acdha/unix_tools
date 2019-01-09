#!/usr/sbin/dtrace -qs

syscall::open:entry,
syscall::stat:entry,
syscall::lstat:entry
/execname == $$1/
{
	printf("%s[%d]: %s %s\n", execname, pid, probefunc, copyinstr(arg0));
}

syscall::rename:entry
/execname == $$1/
{
	printf("%s[%d]: %s %s %s\n", execname, pid, probefunc, copyinstr(arg0), copyinstr(arg1));
}
