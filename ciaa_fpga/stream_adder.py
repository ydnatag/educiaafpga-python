from nmigen import *
from .stream import Stream
from .simple_adder import Adder


class StreamAdder(Elaboratable):
    def __init__(self, n, domain):
        self.sink_a = Stream(n)
        self.sink_b = Stream(n)
        self.source = Stream(n)
        self.n = n
        self.domain = domain

    def elaborate(self, platform):
        m = Module()
        sync = m.d[self.domain]
        comb = m.d.comb

        a = self.sink_a
        b = self.sink_b
        r = self.source

        m.submodules.adder = adder =  Adder(self.n, 'comb')
        comb += [
            adder.a.eq(a.data),
            adder.b.eq(b.data),
        ]

        with m.If(r.accepted()):
            sync += r.valid.eq(0)

        with m.If(a.accepted() & b.accepted()):
            sync += [
                r.data.eq(adder.r), # r.data.eq(a.data + b.data),
                r.valid.eq(1),
            ]
        
        ready_to_receive = (~r.valid) | r.accepted()
        both_valid = a.valid & b.valid

        with m.If(ready_to_receive & both_valid):
            comb += [
                a.ready.eq(1),
                b.ready.eq(1),
            ]
        return m


if __name__ == '__main__':
    from nmigen.cli import main
    core = StreamAdder(10, 'sync')
    ports = [
        field for port in [core.sink_a, core.sink_b, core.source]
              for field in port.fields.values() 
    ]
    main(core, platform=None, ports=ports)

