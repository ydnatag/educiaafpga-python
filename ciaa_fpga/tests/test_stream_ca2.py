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


@cocotb.test()
async def the_test(dut):
    N = 100
    a = StreamDriver(dut, dut.clk, 'sink')
    r = StreamDriver(dut, dut.clk, 'source')
    a.valid <= 0
    r.ready <= 0

    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    trg = RisingEdge(dut.clk)
    await reset(dut)

    bits = len(r.data)
    mask = int('1' * bits, 2)

    input_data = [random.getrandbits(bits) for i in range(N)]
    expected = [((~d) + 1) & mask for d in input_data]

    cocotb.fork(a.send_burps(input_data))
    data = await r.recv_burps(N)
    assert data == expected



def test_stream_ca2():
    from ..stream_ca2 import StreamCa2
    from nmigen_cocotb import run

    core = StreamCa2(4, 'sync')
    run(
        core,
        'ciaa_fpga.tests.test_stream_ca2',
        None,
        ports=[f for port in [core.sink, core.source] for f in port.fields.values()],
        vcd_file='stream_ca2.vcd'
    )

if __name__ == '__main__':
    test_stream_ca2()
