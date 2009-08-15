#!/usr/sbin/dtrace -qs

syscall:::entry {
	self->argstring = "…";
}

syscall::open:entry,
syscall::stat:entry,
syscall::lstat:entry
/execname == $$1/
{
	self->argstring = copyinstr(arg0)
} 

syscall::rename:entry
/execname == $$1/
{
	self->argstring = strjoin(strjoin(copyinstr(arg0), ", "), copyinstr(arg1))
} 

syscall:::return
/execname == $$1 && (int)arg0 == -1/
{
	printf("%s[%d]: %s(%s) = %d\n", execname, pid, probefunc, self->argstring, arg0);	
}