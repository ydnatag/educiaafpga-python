import cocotb
from cocotb.triggers import Timer, RisingEdge
import random


class StreamDriver:
    def __init__(self, dut, clk, prefix):
        setattr(self, 'data', getattr(dut, prefix + '__data'))
        setattr(self, 'valid', getattr(dut, prefix + '__valid'))
        setattr(self, 'ready', getattr(dut, prefix + '__ready'))
        self.re = RisingEdge(clk)

    async def send(self, value):
        self.data <= value
        self.valid <= 1
        await self.re
        while self.ready.value == 0:
            await self.re
        self.valid <= 0

    async def recv(self):
        self.ready <= 1
        await self.re
        while self.valid.value == 0:
            await self.re
        self.ready <= 0
        return self.data.value.integer

    async def send_burst(self, values):
        for v in values:
            await self.send(v)

    async def send_burps(self, values, max_delay=5):
        for v in values:
            delay = random.randrange(max_delay)
            for _ in range(delay):
                await self.re
            await self.send(v)

    async def recv_burst(self, n):
        rv = []
        for _ in range(n):
            v = await self.recv()
            rv.append(v)
        return rv

    async def recv_burps(self, n, max_delay=5):
        rv = []
        for _ in range(n):
            delay = random.randrange(max_delay)
            for _ in range(delay):
                await self.re
            v = await self.recv()
            rv.append(v)
        return rv


