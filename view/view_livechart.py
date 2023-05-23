# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 17:58:15
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 13:59:23


from event_bus import EventBus
from model import Bar, EventType, Order
from view import View, LiveChart
from utility import check_running
from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class LiveChartView(View):
    def __init__(self, bus: EventBus, live_chart: LiveChart) -> None:
        self.bus = bus
        self.live_chart = live_chart
        self.running = False

        self.handler_dict: dict[EventType, callable] = dict()
        self.register(EventType.BAR, self.on_bar)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    @check_running
    def on_bar(self, bar: Bar):
        LOG.debug(f"LiveChartView reveived {bar}")
        self.live_chart.on_bar(bar)

    @check_running
    def on_order_create(self, order: Order):
        pass
