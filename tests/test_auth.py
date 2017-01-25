import unittest
import random

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.auth import User, login
import config


class TestAuth(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_userdef(self):
        u = User.select({'id':1})
        self.assertEquals(u.name, 'pdk')
        self.assertEquals(u.level, 'admin')

    def test_usersearch(self):
        u = login('pdk','admin')



def suite():
    s =  unittest.TestLoader().loadTestsFromTestCase(TestAuth)
    return unittest.TestSuite([s])

if __name__ == '__main__':
    unittest.main()
