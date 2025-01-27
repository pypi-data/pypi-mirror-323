# -*- coding: UTF-8 -*-
import unittest

class SeppUnitTestCase(unittest.TestCase):

    def setUp(self):
        print('setup')

    def tearDown(self):
        print('teardown')

    def test_test1(self):
        print('test_valid 1')

    def test_test2(self):
        print('test_valid 2')

    def test_test3(self):
        print('test_valid 3')

    def test_test4(self):
        print('test_valid 4')