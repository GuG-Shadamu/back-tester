# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-25 02:50:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-25 02:56:06
import unittest
from unittest.mock import Mock


from data_feed import OHLCBarFeed


class TestDataFeed(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = Mock()
        self.OHLCData = Mock()
        self.push_freq = 1
        self.feed = OHLCBarFeed(self.bus, self.OHLCData, self.push_freq)

    def test_start(self):
        pass

    def test_stop(self):
        pass
