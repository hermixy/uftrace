#!/usr/bin/env python

from runtest import TestBase
import subprocess as sp
import os

TDIR='xxx'

class TestCase(TestBase):
    def __init__(self):
        TestBase.__init__(self, 'openclose', """
# DURATION    TID     FUNCTION
            [18343] | main() {
            [18343] |   fopen() {
  86.790 us [18343] |     sys_open();
  89.018 us [18343] |   } /* fopen */
  37.325 us [18343] |   fclose();
 128.387 us [18343] | } /* main */
""")

    def pre(self):
        if os.geteuid() != 0:
            return TestBase.TEST_SKIP
        if os.path.exists('/.dockerenv'):
            return TestBase.TEST_SKIP

        record_cmd = '%s record -k -N %s@kernel -d %s %s' % \
                     (TestBase.uftrace_cmd, 'smp_irq_work_interrupt', TDIR, 't-' + self.name)
        sp.call(record_cmd.split())
        return TestBase.TEST_SUCCESS

    def runcmd(self):
        return '%s replay -F main -D2 -F ^sys_open@kernel -d %s' % (TestBase.uftrace_cmd, TDIR)

    def post(self, ret):
        sp.call(['rm', '-rf', TDIR])
        return ret

    def fixup(self, cflags, result):
        return result.replace('sys_open', 'sys_openat')
