# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 17:58:15
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-27 22:01:37


from event_bus import EventBus
from model import Bar, EventType, Order
from utility import check_running
from log import TaskAdapter, setup_logger

from .core import ChartService, View

LOG = TaskAdapter(setup_logger(), {})


class UpdateChart(View):
    def __init__(self, bus: EventBus, chart_service: ChartService = None) -> None:
        self.bus = bus
        self.chart_service = chart_service
        self.running = False

        self.handler_dict: dict[EventType, callable] = dict()
        self.register(EventType.BAR, self.on_bar)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def associate_service(self, service: ChartService):
        self.chart_service = service

    @check_running
    async def on_bar(self, bar: Bar):
        LOG.debug(f"LiveChartView reveived {bar}")
        if self.chart_service:
            await self.chart_service.on_bar(bar)

    @check_running
    def on_order_create(self, order: Order):
        pass
