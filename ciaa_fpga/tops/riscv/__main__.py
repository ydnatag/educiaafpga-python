import argparse
import importlib

from ...platform import EduCiaaFPGA
from os import path
from nmigen import *
from nmigen_soc import wishbone

from lambdasoc.cpu.minerva import MinervaCPU
from lambdasoc.periph.intc import GenericInterruptController
from lambdasoc.periph.serial import AsyncSerialPeripheral
from lambdasoc.periph.sram import SRAMPeripheral
from lambdasoc.periph.timer import TimerPeripheral
from lambdasoc.soc.cpu import CPUSoC

import subprocess


class RiscVSoC(CPUSoC, Elaboratable):
    def __init__(self, *, reset_addr, clk_freq,
                 rom_addr, rom_size,
                 ram_addr, ram_size,
                 uart_addr, uart_divisor, uart_pins,
                 timer_addr, timer_width):
        self._arbiter = wishbone.Arbiter(addr_width=30, data_width=32, granularity=8,
                                         features={"cti", "bte"})
        self._decoder = wishbone.Decoder(addr_width=30, data_width=32, granularity=8,
                                         features={"cti", "bte"})

        self.cpu = MinervaCPU(reset_address=reset_addr)
        self._arbiter.add(self.cpu.ibus)
        self._arbiter.add(self.cpu.dbus)

        self.rom = SRAMPeripheral(size=rom_size, writable=False)
        self._decoder.add(self.rom.bus, addr=rom_addr)

        self.ram = SRAMPeripheral(size=ram_size)
        self._decoder.add(self.ram.bus, addr=ram_addr)

        self.uart = AsyncSerialPeripheral(divisor=uart_divisor, pins=uart_pins)
        self._decoder.add(self.uart.bus, addr=uart_addr)

        self.timer = TimerPeripheral(width=timer_width)
        self._decoder.add(self.timer.bus, addr=timer_addr)

        self.intc = GenericInterruptController(width=len(self.cpu.ip))
        self.intc.add_irq(self.timer.irq, 0)
        self.intc.add_irq(self.uart .irq, 1)

        self.memory_map = self._decoder.bus.memory_map

        self.clk_freq = clk_freq

    def compile_fw(self, dir):
        dirname = path.dirname(__file__)
        sources = [path.join(dirname, f) for f in ['crt0.S', 'main.c']]
        linker = path.join(dirname, 'linker.ld')
        cmd = 'riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -g -Os -Iinclude -T{} -nostdlib {} -o {}/{}' 
        cmd = cmd.format(linker, ' '.join(sources), dir, 'boot.elf')
        subprocess.check_call(cmd.split(' '))

        cmd = 'riscv64-unknown-elf-objcopy -O binary {dir:}/boot.elf {dir:}/boot.bin'
        cmd = cmd.format(dir=dir)
        subprocess.check_call(cmd.split(' '))


    def elaborate(self, platform):
        m = Module()

        clk = platform.request('clk12', 0)
        clk42 = Signal()
        locked = Signal()
        
        m.domains += ClockDomain('sync')
        m.submodules.pll = Instance(
            'SB_PLL40_CORE',
            p_FEEDBACK_PATH = "SIMPLE",
            p_DIVR = 0,
            p_DIVF = 55,
            p_DIVQ = 4,
            p_FILTER_RANGE = 1,
            o_LOCK = locked,
            i_RESETB = Const(1, 1),
            i_BYPASS = Const(0, 1),
            i_REFERENCECLK = clk,
            o_PLLOUTCORE = clk42,
        )
        m.d.comb += [
            ClockSignal('sync').eq(clk42),
            ResetSignal('sync').eq(~locked),
        ]
        platform.add_clock_constraint(clk42, 42e6)

        m.submodules.arbiter = self._arbiter
        m.submodules.cpu     = self.cpu

        m.submodules.decoder = self._decoder
        m.submodules.rom     = self.rom
        m.submodules.ram     = self.ram
        m.submodules.uart    = self.uart
        m.submodules.timer   = self.timer
        m.submodules.intc    = self.intc

        m.d.comb += [
            self._arbiter.bus.connect(self._decoder.bus),
            self.cpu.ip.eq(self.intc.ip),
        ]

        return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    platform = EduCiaaFPGA()

    uart_divisor = int(42e6 // 115200)
    uart_pins = platform.request("uart", 0)

    soc = RiscVSoC(
         reset_addr=0x00000000, clk_freq=int(42e6),
           rom_addr=0x00000000, rom_size=0x1000,
           ram_addr=0x00001000, ram_size=0x1000,
          uart_addr=0x00002000, uart_divisor=uart_divisor, uart_pins=uart_pins,
         timer_addr=0x00003000, timer_width=32,
    )

    soc.compile_fw('build')
    boot_bin = "build/boot.bin"
    with open(boot_bin, "rb") as f:
        words = iter(lambda: f.read(soc.cpu.data_width // 8), b'')
        boot_rom  = [int.from_bytes(w, soc.cpu.byteorder) for w in words]
    soc.rom.init = boot_rom
    platform.build(soc, do_program=True)

