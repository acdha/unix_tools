#!/usr/sbin/dtrace -s
/*
  Traces system locking activity and attempts to print the process and filename for each lock request

  Accounts for locks resulting from the following calls:
	flock()
	fcntl(SETLK|SETLKW)
	open(..., O_SHLOCK|O_EXLOCK)
*/

#pragma D option quiet

BEGIN {
	start = timestamp;
}

ERROR {
	printf("dtrace error in %s[%d] error on probe ID %d action #%d at DIF offset %d: %d : %x\n", execname, pid, arg1, arg2, arg3, arg4, arg5)
}

syscall::flock:entry
/ (arg1 & 1) || (arg1 & 2) /
{
	@locks[execname, pid, probefunc, arg1 & 1 ? "LOCK_SH" : "LOCK_EX", fds[arg0].fi_pathname ] = count();
} 

syscall::fcntl:entry
/ (arg1 == 8) || (arg1 == 9)/
{
	/* F_SETLK / F_SETLKW */
	@locks[execname, pid, probefunc, arg1 == 8 ? "F_SETLK" : "F_SETLKW", fds[arg0].fi_pathname ] = count();
} 

syscall::open:entry
/ (arg1 & O_SHLOCK) || (arg1 & O_EXLOCK) /
{
	self->locktype = arg1
} 

syscall::open:return
/ arg0 >= 0 /
{
	@locks[execname, pid, probefunc, self->locktype & O_SHLOCK ? "O_SHLOCK" : "O_EXLOCK", fds[arg0].fi_pathname ] = count();
}

tick-$1 {
	normalize(@locks, (timestamp - start) / 1000000000);
	printa("%16s[%u]\t%8s %8s %s\n", @locks);
	trunc(@locks);
	printf("----- %Y\n", walltimestamp);
}
