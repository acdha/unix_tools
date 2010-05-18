#!/usr/sbin/dtrace -qs

.Python:PyEval_EvalFrameEx:function-entry
{
	    printf("file:%s[%d]: (parent=%s)\n", copyinstr(arg0), arg2, copyinstr(arg1) );
}
