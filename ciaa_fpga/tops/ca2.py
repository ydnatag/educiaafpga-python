from nmigen import *
from ..platform import EduCiaaFPGA
from ..stream_ca2 import StreamCa2

class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        clk = platform.request(platform.default_clk)
        m.domains += ClockDomain('sync')
        m.d.comb += [
            ClockSignal('sync').eq(clk),
            ResetSignal('sync').eq(0),
        ]

        leds = Cat(platform.request('led', i, dir='o').o for i in range(4))
        buttons = Cat(platform.request('button', i, dir='i').i for i in range(4))

        m.submodules.ca2 = ca2 = StreamCa2(len(leds))
        m.d.comb += [
            ca2.sink.data.eq(buttons),
            ca2.sink.valid.eq(1),
            ca2.source.ready.eq(1),
        ]

        with m.If(ca2.source.accepted()):
            m.d.sync += leds.eq(ca2.source.data)


        return m

core = Top()
plat = EduCiaaFPGA()
plat.build(core, do_program=True)
