from nmigen import *
from nmigen_stdio.serial import AsyncSerial
from .stream import Stream

class StreamUart(Elaboratable):
    def __init__(self, *, pins, divisor):
        self.pins = pins
        self.divisor = divisor
        self.sink = Stream(8)
        self.source = Stream(8)

    def elaborate(self, platform):
        m = Module()
        m.submodules.uart = uart = AsyncSerial(pins=self.pins, divisor=self.divisor)

        with m.If(self.source.accepted()):
            m.d.sync += self.source.valid.eq(0)
        with m.Else():
            m.d.sync += [
                self.source.data.eq(uart.rx.data),
                self.source.valid.eq(uart.rx.rdy),
            ]

        m.d.comb += [
            uart.tx.data.eq(self.sink.data),
            uart.tx.ack.eq(self.sink.valid),
            self.sink.ready.eq(uart.tx.rdy),
            uart.rx.ack.eq(1),
        ]
        
        return m

