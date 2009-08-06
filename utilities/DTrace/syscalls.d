#!/usr/sbin/dtrace -s

#pragma D option quiet

/*
 * Count the syscalls a process is making as a stat tool
 *
 * $1 time to wait (eg 10s)
 * $2 target pid
 */

syscall:::entry /pid == $2/ {
	@[probefunc] = count();}

tick-$1 {
	printa(@);
	clear(@);
}
