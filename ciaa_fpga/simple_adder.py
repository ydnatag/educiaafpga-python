from nmigen import *


class Adder(Elaboratable):
    def __init__(self, n, domain='sync'):
        self.a = Signal(n)
        self.b = Signal(n)
        self.r = Signal(n)
        self.domain = domain

    def elaborate(self, platform):
        m = Module()
        domain = m.d[self.domain]
        domain += self.r.eq(self.a + self.b)
        return m


if __name__ == '__main__':
    from nmigen.cli import main
    core = Adder(10, 'comb')
    main(core, platform=None, ports=[core.a, core.b, core.r])
