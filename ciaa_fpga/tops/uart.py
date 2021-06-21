from nmigen import *
from ..stream import Stream
from ..stream_uart import StreamUart
from ..platform import EduCiaaFPGA


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        clk = platform.request(platform.default_clk)
        m.domains += ClockDomain('sync')
        m.d.comb += ClockSignal('sync').eq(clk)

        clk_freq = platform.default_clk_frequency
        baudrate = 115200
        divisor = int(clk_freq // baudrate)

        leds = Cat(platform.request('led', i, dir='o').o for i in range(4))
        m.submodules.uart = uart = StreamUart(pins=platform.request('uart', 0), divisor=divisor)

        m.d.comb += uart.source.connect_downstream(uart.sink)
        
        with m.If(uart.source.accepted()):
            m.d.sync += leds.eq(uart.source.data)

        return m


core = Top()
plat = EduCiaaFPGA()
plat.build(core, do_program=True)

