from nmigen import *
from .stream import Stream

class StreamInverter(Elaboratable):
    def __init__(self, n, domain='sync'):
        self.sink = Stream(n)
        self.source = Stream(n)
        self.n = n
        self.domain = domain

    def elaborate(self, platform):
        m = Module()
        sync = m.d[self.domain]
        comb = m.d.comb

        with m.If(self.source.accepted()):
            sync += self.source.valid.eq(0)

        with m.If(self.sink.accepted()):
            sync += [
                self.source.data.eq(~self.sink.data),
                self.source.valid.eq(1),
            ]
        
        with m.If((~self.source.valid) | self.source.accepted()):
            comb += self.sink.ready.eq(1)
        return m

if __name__ == '__main__':
    from nmigen.cli import main
    core = StreamInverter(10, 'sync')
    ports = [
        *list(core.sink.fields.values()),
        *list(core.source.fields.values()),
    ]
    main(core, platform=None, ports=ports)

