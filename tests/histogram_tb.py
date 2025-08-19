import os
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner

VERILOG_FILE_NAME = "histogram_mem.sv"
MODULE_NAME ="histogram_mem"
PYTHON_FILE_NAME="histogram_tb"


async def Reset(reset,clk,cycles=4):
    reset.value = 1
    for i in range(cycles):
        await RisingEdge(clk)
    reset.value = 0
    await Timer(100,units="ps")


async def load_image(clk,data,valid,last,ready):
    if(ready.value ==0):
        await RisingEdge(ready)
    data.value = 0xFF
    valid.value = 1
    for i in range(4):
        await RisingEdge(clk)
    data.value = 0x0F
    valid.value = 1
    for i in range(2):
        await RisingEdge(clk)
    data.value = 0x00
    valid.value = 1
    last.value = 1
    await RisingEdge(clk)
    data.value = 0x00
    valid.value = 0
    last.value = 0


async def read_histogram(uut,histo):
    for i in range (256):
        value = histo[i].value
        match i:
            case 0:
                assert value == 1, (f"value for indiex {i} should be 1, reading back {value}")
            case 15:
                assert value == 2, (f"value for indiex {i} should be 2, reading back {value}")
            case 255:
                assert value == 4, (f"value for indiex {i} should be 4, reading back {value}")
            case _:
                assert value == 0, (f"value for indiex {i} should be 0, reading back {value}")
          
            
        #uut._log.info("index=" + str(i) +" value="+ str(hex(value)))


@cocotb.test()
async def memory_test(uut):
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    await Timer(100,units="ps")
    await Reset(uut.i_reset,uut.i_clk)
    await Timer(4,units="ns")
    await load_image(uut.i_clk,uut.i_data,uut.i_valid,uut.i_last,uut.o_ready)
    await Timer(4,units="ns")
    await read_histogram(uut,uut.o_histogram)
    await Timer(1,units="ns")

    
def test_histogram_runner():
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
    test_histogram_runner()