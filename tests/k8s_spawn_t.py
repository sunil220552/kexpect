import io
from pdb import set_trace
import kexpect

from re import S, T
import unittest
from kexpect.k8s_spawn import spawn
from kexpect.container_info import containerInfo
from kexpect import ExceptionKexpect, TIMEOUT, ExceptionK8sAPI

class SpawnPositiveCases(unittest.TestCase):
    def setUp(self):
        container_info = containerInfo(pod='static-web', container='web',\
            namespace='default', shell='sh', prompt='#')
        self._shell = spawn(container_info)
        self._log_file = io.StringIO()
        self._shell._logfile = self._log_file

    def tearDown(self):
        self._shell.exit()

    def test_basic_command(self):
        self._shell.sendline('expr 1980 + 7')
        self._shell.expect_shell_prompt(30)
        ret_code = self._shell.get_exit_status()
        self._log_file.seek(0)
        self.assertIsInstance(ret_code, int)
        self.assertEqual(0, ret_code)
        self.assertIn('1987', self._log_file.read())

    def test_shell_prompt_timeout(self):
        self._shell.sendline('echo 0')
        flag = False
        try:
            self._shell.expect_shell_prompt(0)
            flag = True
        except Exception as exp:
            self.assertIsInstance(exp, TIMEOUT)
        self.assertEqual(False, flag)

class SpawnNegativeCases(unittest.TestCase):
    def test_invalid_pod(self):
        flag = False
        try:
            container_info = containerInfo(pod='Invalid', container='web',\
                namespace='default', shell='sh', prompt='#')
            self._shell = spawn(container_info)
            flag = T
        except Exception as exp:
            self.assertIsInstance(exp, ExceptionK8sAPI)
        self.assertEqual(False, flag)
