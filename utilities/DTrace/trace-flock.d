#!/usr/sbin/dtrace -s
syscall::flock:entry, syscall::flock:return
{
   trace(pid);
   trace(execname);
} 
