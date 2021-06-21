from nmigen import *
from .stream import Stream
from .stream_adder import StreamAdder
from .stream_inverter import StreamInverter


class StreamCa2(Elaboratable):
    def __init__(self, n, domain='sync'):
        self.sink = Stream(n)
        self.source = Stream(n)
        self.domain = domain
        self.n = n

    def elaborate(self, platform):
        m = Module()
        m.submodules.inverter = inverter = StreamInverter(self.n, self.domain)
        m.submodules.adder = adder = StreamAdder(self.n, self.domain)
        m.d.comb += [
            self.sink.connect_downstream(inverter.sink),
            inverter.source.connect_downstream(adder.sink_a),
            adder.source.connect_downstream(self.source),
            adder.sink_b.data.eq(1),
            adder.sink_b.valid.eq(1),
        ]
        return m


if __name__ == '__main__':
    from nmigen.cli import main
    core = StreamCa2(10)
    ports = [
        *list(core.sink.fields.values()),
        *list(core.source.fields.values()),
    ]
    main(core, platform=None, ports=ports)
