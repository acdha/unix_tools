#!/usr/sbin/dtrace -s

#pragma D option quiet

BEGIN {
	start = timestamp;
	go = 1;
}

proc:::exec-success
/execname == "gnome-session"/
{
        start = timestamp;
        go = 1;
}

io:::start
/go/
{
        printf("%10d { -> I/O %d %s %s %s }\n",
            (timestamp - start) / 1000000, pid, execname,
            args[0]->b_flags & B_READ ? "reads" : "writes",
            args[2]->fi_pathname);
}

io:::done
/go/
{
        printf("%10d { <- I/O to %s }\n",
            (timestamp - start) / 1000000, args[2]->fi_pathname);
}

io:::start
/go && ((struct buf *)arg0)->b_file != NULL &&
    ((struct buf *)arg0)->b_file->v_path == NULL/
{
        printf("%10s   (vp %p)\n", "", ((struct buf *)arg0)->b_file);
}

io:::start
/go/
{
        @apps[execname] = count();
        @files[args[2]->fi_pathname] = count();
        @appsfiles[execname, args[2]->fi_pathname] = count();
}

proc:::exec
/go/
{
        self->parent = execname;
}

proc:::exec-success
/self->parent != NULL/
{
        printf("%10d -> %d %s (from %d %s)\n",
            (timestamp - start) / 1000000, pid, execname,
            curpsinfo->pr_ppid, self->parent);
        self->parent = NULL;
}

proc:::exit
/go/
{
        printf("%10d <- %d %s\n",
            (timestamp - start) / 1000000, pid, execname);

}

profile-101hz
/go && arg1 != NULL/
{
        printf("%10d [ %d %s ]\n",
            (timestamp - start) / 1000000, pid, execname);
}

profile-101hz
/go && arg1 == NULL &&
  (curlwpsinfo->pr_flag & PR_IDLE)/
{
        printf("%10d [ idle ]\n",
            (timestamp - start) / 1000000);
}

END
{
        printf("\n  %-72s %s\n", "APPLICATION", "I/Os");
        printa("  %-72s %@d\n", @apps);
        printf("\n  %-72s %s\n", "FILE", "I/Os");
        printa("  %-72s %@d\n", @files);
        printf("\n  %-16s %-55s %s\n", "APPLICATION", "FILE", "I/Os");
        printa("  %-16s %-55s %@d\n", @appsfiles);
}