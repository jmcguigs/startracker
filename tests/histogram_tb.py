import os
import sys
import random
from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner

VERILOG_FILE_NAME = "histogram_mem.sv"
MODULE_NAME ="histogram_mem"
PYTHON_FILE_NAME="histogram_tb"

async def clk_gen(clk,half_clk_cycle=1):
    clk.value = half_clk_cycle
    await Timer(1,units="ns")
    clk.value = half_clk_cycle
    await Timer(1,units="ns")

async def Reset(uut,reset,clk,cycles=4):
    reset.value = 1
    for i in range(cycles):
        uut._log.info("Test me0")
        await RisingEdge(clk)
        uut._log.info("Test me1")
    reset.value = 0

    


@cocotb.test()
async def memory_test(uut):
    cocotb.start_soon(clk_gen(uut.i_clk))
    await Timer(100,units="ps")
    await Reset(uut,uut.i_reset,uut.i_clk)
    await Timer(4,units="ns")

    



def test_counter_runner():
    """
    Simulate the 4-bit binary counter using cocotb and the specified HDL language.
    """
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable

    
    sources = [proj_path / "hdl" / VERILOG_FILE_NAME]

    build_test_args = []

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=MODULE_NAME,
        always=True,
        build_args=build_test_args
    )
    runner.test(
        hdl_toplevel=MODULE_NAME, test_module=PYTHON_FILE_NAME, test_args=build_test_args
    )


if __name__ == "__main__":
    test_counter_runner()