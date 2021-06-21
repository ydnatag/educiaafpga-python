import pytest
import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
import random

async def reset(dut):
    dut.rst <= 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst <= 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def the_test(dut):
    dut.a <= 0
    dut.b <= 0
    if hasattr(dut, 'clk'):
        cocotb.fork(Clock(dut.clk, 10, 'ns').start())
        trg = RisingEdge(dut.clk)
        await reset(dut)
    else:
        trg = Timer(10, 'ns')
    bits = len(dut.r)
    mask = int('1' * bits, 2)
    input_a = [random.getrandbits(bits) for i in range(100)]
    input_b = [random.getrandbits(bits) for i in range(100)]
    
    for a, b in zip(input_a, input_b):
        dut.a <= a
        dut.b <= b
        await trg
        await trg
        assert dut.r.value == (a + b) & mask


@pytest.mark.parametrize('domain', ['sync', 'comb'])
def test_adder(domain):
    from ..simple_adder import Adder
    from nmigen_cocotb import run

    core = Adder(10, domain=domain)
    run(
        core,
        'ciaa_fpga.tests.test_simple_adder',
        None,
        ports=[core.a, core.b, core.r],
        vcd_file='adder_' + domain + '.vcd'
    )

if __name__ == '__main__':
    test_adder('sync')
    test_adder('comb')
