import pytest
import cocotb
from .stream import StreamDriver
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from cocotb.regression import TestFactory
import random


async def reset(dut):
    dut.rst <= 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst <= 0
    await RisingEdge(dut.clk)


async def the_test(dut, burps):
    N = 100
    a = StreamDriver(dut, dut.clk, 'sink_a')
    b = StreamDriver(dut, dut.clk, 'sink_b')
    r = StreamDriver(dut, dut.clk, 'source')
    a.valid <= 0
    b.valid <= 0
    r.ready <= 0

    async def send(stream, data):
        if burps:
            coro = stream.send_burps
        else:
            coro = stream.send_burst
        await coro(data)

    async def recv(stream, n):
        if burps:
            coro = stream.recv_burps
        else:
            coro = stream.recv_burst
        return await coro(n)

    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    trg = RisingEdge(dut.clk)
    await reset(dut)

    bits = len(r.data)
    mask = int('1' * bits, 2)
    input_a = [random.getrandbits(bits) for i in range(N)]
    input_b = [random.getrandbits(bits) for i in range(N)]
    expected = [(a + b) & mask for a, b in zip(input_a, input_b)]

    cocotb.fork(send(a, input_a))
    cocotb.fork(send(b, input_b))
    data = await recv(r, N)
    assert data == expected

tf = TestFactory(the_test)
tf.add_option('burps', [True, False])
tf.generate_tests()


def test_stream_adder():
    from ..stream_adder import StreamAdder
    from nmigen_cocotb import run

    core = StreamAdder(4, 'sync')
    run(
        core,
        'ciaa_fpga.tests.test_stream_adder',
        None,
        ports=[f for port in [core.sink_a, core.sink_b, core.source] for f in port.fields.values()],
        vcd_file='stream_adder.vcd'
    )

if __name__ == '__main__':
    test_stream_adder()
