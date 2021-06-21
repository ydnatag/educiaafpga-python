from nmigen import Record
from nmigen import tracer

class Stream(Record):
    def __init__(self, n, name=None, src_loc_at=0):
        if name is None:
            name = tracer.get_var_name(depth=2 + src_loc_at, default=None)
        super().__init__([('data', n), ('valid', 1), ('ready', 1)], name=name, src_loc_at=src_loc_at)

    def connect_downstream(self, other):
        return [
            other.data.eq(self.data),
            other.valid.eq(self.valid),
            self.ready.eq(other.ready),
        ]

    def accepted(self):
        return self.valid & self.ready

    class CocotbDriver:
        def __init__(self, n, dut, clk):
            pass
