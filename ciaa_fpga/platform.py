from nmigen.vendor.lattice_ice40 import *
from nmigen_boards.resources import *
from nmigen.build import *
import os
import subprocess

class EduCiaaFPGA(LatticeICE40Platform):
    device      = "iCE40HX4K"
    package     = "TQ144"
    default_clk = "clk12"
    resources   = [
        Resource("clk12", 0, Pins("94", dir="i"),
                 Clock(12e6), Attrs(GLOBAL=True, IO_STANDARD="SB_LVCMOS")),

        *LEDResources(
            pins="1 2 3 4",
            attrs=Attrs(IO_STANDARD="SB_LVCMOS")
        ),

        *ButtonResources(
            pins="31 32 33 34",
            invert=True, 
            attrs=Attrs(IO_STANDARD="SB_LVCMOS")
        ),

        UARTResource(0,
            rx="55", tx="56", rts="60", cts="61", dtr="62", dsr="63", dcd="64",
            attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1),
            role="dce"
        ),
    ]
    connectors = []

    def toolchain_program(self, products, name):
        iceprog = os.environ.get("ICEPROG", "iceprog")
        with products.extract("{}.bin".format(name)) as bitstream_filename:
            subprocess.check_call([iceprog, bitstream_filename])

