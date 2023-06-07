# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 17:58:15
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:51:47


from EventBus import EventBus
from log.TaskAdapter import TaskAdapter
from model import Bar, EventType, Order
from log import LOG
from engine.EventHandler import EventHandler
from .View import View

from .ChartService import ChartService


class UpdateChart(View):
    def __init__(self, bus: EventBus, chart_service: ChartService = None) -> None:
        super().__init__(bus)
        self.chart_service = chart_service

    def associate_service(self, service: ChartService):
        self.chart_service = service

    @EventHandler.register(EventType.BAR)
    async def on_bar(self, bar: Bar):
        LOG.debug(f"LiveChartView reveived {bar}")
        if self.chart_service:
            await self.chart_service.on_bar(bar)

    def on_order_create(self, order: Order):
        pass
