+++
title = "reveal-hugo"
description = "A Hugo theme for creating Reveal.js presentations"
outputs = ["Reveal"]
[reveal_hugo]
custom_theme = "reveal-hugo/themes/robot-lung.css"
margin = 0.2
highlight_theme = "color-brewer"
transition = "slide"
transition_speed = "fast"
[reveal_hugo.templates.hotpink]
class = "hotpink"
background = "#FF4081"
+++

{{< figure src="http://www.trece.com.py/uploads/swp/gfftv8/media/5ee7dd8ea97ed87e3df8bc9f.jpeg" width="20%" >}} 
# Un mundo mejor
### Programando FPGAs en PYTHON

Andrés Demski

https://github.com/andresdemski/educiaafpga-python

---

## Temario

* Motivación
* Diseño: nMigen
* Simulación: cocotb
* Buildeo: nMigen
* Bonus: Riscv + nMigen + ciaa fpga

---

## Motivación: Por qué Python?

* Verilog y VHDL :poop:
* HDL con OOP
* Velocidad de desarrollo
* Comunidad
* Testeo
* Acercar SW y HDL
* Package manager
* Mantenibilidad

---

{{% section %}}

## HDL Flow

{{< figure src="./flow.svg" width="85%" >}} 

---

## newHDLs


SystemC, VisualHDL, concat, CλaSH, pipelineDSL, Bluespec, jhdl PSHDL reqack, 
hdl-js, shdl, Julia-Verilog, HWT, garnet, magma, migen, MyHDL, **nMigen**, 
Pyrope, PyRTL, PyMTL, veriloggen, RHDL hoodlum, kaze, chisel, SpinalHDL, 
Quokka, 

<small>
</small>

https://github.com/drom/awesome-hdl

---

## nMigen

* Creador: [@whitequark](https://github.com/whitequark)
* Primer release: Octubre 2019
* Ultimo release: Febrero 2020
* Repositorio: https://github.com/nmigen/nmigen/
* Documentación: https://nmigen.info/nmigen/latest/

---

## Que es nMigen?

* Herramienta de diseño
* Herramienta de simulación
* Herramienta de buildeo

---

# nMigen flow

{{< figure src="./nmigen_flow.svg" width="60%" >}} 

---

# Sintaxis

---
## Elaboratable

```python
from nmigen import *

class TheCore(Elaboratable)
    def __init__(self):
        <insert your code here>

    def elaborate(self, platform):
        m = Module()
        <insert your code here>
        return m
```

---
## Asignaciones

```python
from nmigen import *

class TheCore(Elaboratable)
    def __init__(self):
        self.d = Signal()
        self.q = Signal(reset=0)
        self.w = Signal()

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.q.eq(self.d) # sincronica
        m.d.comb += self.w.es(self.d) # combinacional
        return m
```
---

## Operaciones

```python
# Signals
a = Signal(8)
a = Signal(unsigned(8))
a = Signal(signed(8))
a = Signal(..., reset=reset_value)
b = Signal()

# Logicas
~a, a & b, a | b, a ^ b, a >> b, a << b
a.rotate_right(i), a.rotate_left(i), 
a.all(), a.any(), a.xor(), a.bool()

# Aritmeticas
a + b, a - b
a.as_signed(), a.as_unsigned()

# Bits
len(a), a[i:j:k], iter(a),
a.bit_select(b, width), a.word_select(b, width),
Cat(a, b), Repl(a, n)

# Comparación
a > b, a < b , a <= b, a >=b, a == b, a != b
```

---

## If

```python
def elaborate(self, platform):
    m = Module()

    with m.If(<condition>):
        m.d.comb += [ ... ]
        m.d.sync += [ ... ]

        with m.If(<other-condition>)
            m.d.comb += [ ... ]
            m.d.sync += [ ... ]

    with m.Elif(<other-other-condition):
        m.d.comb += [ ... ]
        m.d.sync += [ ... ]

    with m.Else():
        m.d.comb += [ ... ]
        m.d.sync += [ ... ]
    return m
```

---

## Switch-Case

```python
def elaborate(self, platform):
    m = Module()
    with m.Switch(<signal>):
        with m.Case(<case>):
            <insert code here>

        for i in range(10):
            with m.Case(i):
                <insert code here>

        with m.Default():
            <insert code here>
    return m
```

---

## FSM

```python
def elaborate(self, platform):
    m = Module()

    with m.FSM(domain=self.domain) as fsm:
        with m.State('IDLE'):
            with m.If(<condition>):
                m.next = 'RUN'

        with m.State('RUN'):
            with m.If(<other-condition>):
                m.d.sync += [ ... ]
                m.d.comb += [ ... ]
    return m
```

---

## Records

```python

class TheCore(Elaboratable):
    def __init__(self, n):
        self.stream = Record([('data', n), ('valid', 1), ('ready', 1)])
    
    def elaborate(self, platform):
        m = Module()
        cnt = Signal.like(self.stream.data)
        m.d.comb += self.stream.valid.eq(1)
        with m.If(self.stream.valid & self.stream.ready):
            m.d.sync += self.stream.data.eq(self.stream.data + 1)
        return m
```

---

## Submodules

```python
def TheCore(Elaboratable):
    ...
def elaborate(self, platform):
    m = Module()
    m.submodules.other = other = OtherCore(self.argument)
    m.d.comb += [
        self.o.eq(other.o),
        other.i.eq(self.i),
    ]
    return m
```

---

## Instance

```python
def elaborate(self, platform):
    m = Module()
    m.submodules.other = Instance(
        'non_nmigen_core',
        a_ATTRIBUTE = "TRUE",
        p_PARAMETER = 5,
        o_OUTPUT_SIGNAL = self.a,
        i_INPUT_SIGNAL = self.b,
        io_INOUT_SIGNAL = self.c,
    )

    with open('path/to/verilog/file.v', 'r') as f:
        platform.add_file('file.v', f.read())
    return m
```
---

{{< figure src="https://www.unilad.co.uk/cdn-cgi/image/width=648,quality=70,format=jpeg,fit=pad,dpr=1/https%3A%2F%2Fwww.unilad.co.uk%2Fwp-content%2Fuploads%2F2020%2F12%2F122091216_194906708666485_1155858819270838587_o.jpg" width="40%" >}} 
# Ejemplos!!!

{{% /section %}}

---

{{% section %}}
# Simulación

---

## Cocotb

* Primer release: Julio 2013
* Ultimo release: Mayo 2021
* Repositorio: https://github.com/cocotb/cocotb/
* Documentación: https://docs.cocotb.org

---

## Qué es COCOTB?

{{< figure src="https://docs.cocotb.org/en/stable/_images/cocotb_overview.svg" width="85%" >}} 

---

## Test

```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def the_test(dut):
    await Timer(10, 'ns')

def test_the_core():
    from nmigen_cocotb import run as run_test
    core = TheCore()
    platform = None
    ports = [core.a, core.b]
    run_test(
        core,
        'python.path.to.this.module',
        platform,
        ports,
        vcd_file='./the_core.vcd'
    )

if __name__ == '__main__':
    test_the_core()
```
---

## Acceder a señales

```python
@cocotb.test()
async def the_test(dut):
    signal_a = dut.a
    value_a = dut.a.value
    value_a = dut.a.value.integer
    value_a = dut.a.value.signed_integer
    value_a = dut.a.value.binstr

    dut.a <= 5
    dut.a <= -5
```

---

## Triggers

```python
await Timer(time, units)
await RisingEdge(signal)
await FallingEdge(signal)
await First(*triggers)
await Combine(*triggers)
```

--- 

## Coroutines

```python
async def reset(dut):
    dut.rst <= 1
    await Timer(100, 'ns')
    dut.rst <= 0
    await Timer(100, 'ns')

await def set_value(dut, value):
    dut.a <= value
    await Timer(10, 'ns')

await def read_value(dut):
    await Timer(10, 'ns')
    return dut.b.value

@cocotb.test()
async def the_test(dut):
    await reset(dut)
    await set_value(dut, 5)
    value = await read_value(dut)
    assert value == 10
```

--- 

## Fork

```python
import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

async reset(dut):
    dut.rst <= 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst <= 0
    await RisingEdge(dut.clk)

async def the_test(dut):
    cocotb.fork(Clock(dut.clk, 10, 'ns').start()) # Clock generator
    cocotb.fork(reset(dut)) # await reset(dut)
    for _ in range(100):
        await RisingEdge(dut.clk)
```

---

{{< figure src="https://i2.wp.com/allhtaccess.info/wp-content/uploads/2018/03/programming.gif?fit=1281%2C716&ssl=1" width="85%" >}} 
## MAS EJEMPLOS!!

{{% /section %}}

---

{{% section %}}


# nMigen build

---

# Platform

```python
from nmigen.vendor.lattice_ice40 import *
from nmigen.build import *

class EduCiaaFPGA(LatticeICE40Platform):
    device = "iCE40HX4K"
    package = "TQ144"
    default_clk = "clk12"
    resources = [
        Resource("clk12", 0, Pins("94", dir="i"), Clock(12e6), Attrs(GLOBAL=True, IO_STANDARD="SB_LVCMOS")),
        Resource("uart", 0, 
            Subsignal('rx', Pins("55", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
            Subsignal('tx', Pins("56", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        )
    ]
    connectors = [ Connector('con', 0, ...) ....]
```

---

## Plataformas soportadas

* Intel (quartus)
* Lattice ECP5 (yosys + nextpnr y diamond)
* Lattice ICE40 (yosys + nextpnr y icecube2)
* Lattice MachX02-X03 (diamond)
* quicklogic (symbiflow)
* Xilinx 7 series (vivado y symbiflow)
* Xilinx spartan3/6 (ise)
* Xilinx Ultrascale (vivado)


--- 

## Placas soportadas

fomu_pvt, machxo3_sk, arty_a7, te0714_03_50_2I, ulx3s, de0, arrow_deca,
mister, ecpix5, microzed_z010, chameleon96, sk_xc6slx9, ecp5_5g_evn, zturn_lite_z010,
upduino_v1, de1_soc, quickfeather, blackice_ii, microzed_z020, de0_cv, rz_easyfpga_a2_2,
tinyfpga_ax1, mercury, ice40_hx8k_b_evn, nexys4ddr, kcu105, icebreaker, ice40_up5k_b_evn,
atlys, upduino_v2, ice40_hx1k_blink_evn, numato_mimas, orangecrab_r0_2, zturn_lite_z007s,
de10_lite, de10_nano, nandland_go, arty_z7, genesys2, versa_ecp5, kc705, tinyfpga_ax2,
versa_ecp5_5g, supercon19badge, icebreaker_bitsy, tinyfpga_bx, fomu_hacker, arty_s7,
blackice, alchitry_au, icestick, orangecrab_r0_1

---

## Pedir un recurso

```python
class Top(Elaboratable):
    def __init__(self, *args, **kwargs):
        <insert code here>
 
    def elaborate(self, platform):
        m = Module()
        led = platform.request('led', 0)
        m.d.sync += led.eq(~led)
        return m
    
```

---

## Crear un dominio de clock

```python
class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        clk = platform.request('clk12', 0)
        rst = platform.request('button', 0)
        m.domains += ClockDomain('sync')
        m.d.comb += [
            ClockSignal('sync').eq(clk),
            ClockReset('sync').eq(rst),
        ]
        ...
        return m
```

---

## Build!

```python
core = TheCore(args)
plat = EduCiaaFPGA()
plat.build(core, do_program=True)
```

---

{{< figure src="https://66.media.tumblr.com/tumblr_m7v0lxN0po1rn95k2o1_500.gif" width="40%" >}} 
## SII!! MAS EJEMPLOS!!

{{% /section %}}

---

# ¿Preguntas?

---

# Muchas gracias!


andresdemski@gmail.com

https://github.com/andresdemski/educiaafpga-python

https://github.com/andresdemski

https://www.linkedin.com/in/ademski/
