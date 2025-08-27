import os
import sys
from pathlib import Path

from utils.test_common import Test
import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner
from cocotb.binary import BinaryValue

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
    histogram = 256*[0]
    if(ready.value ==0):
        await RisingEdge(ready)
    data.value = 0xFF
    valid.value = 1
    for i in range(4):
        histogram[255] += 1
        await RisingEdge(clk)
    data.value = 0x0F
    valid.value = 1
    for i in range(2):
        histogram[15] += 1
        await RisingEdge(clk)
    data.value = 0x00
    valid.value = 1
    last.value = 1
    histogram[0] += 1
    await RisingEdge(clk)
    data.value = 0x00
    valid.value = 0
    last.value = 0
    
    return histogram


async def read_histogram(histo,expected,):
    
        #binexp = BinaryValue(expected,16*256)
        expected_bin = BinaryValue(int(expected),16*256)
        actual = hex(int(histo.value))
        assert actual == hex(expected), (f"\n actual \n{actual:x}\n\n expected\n {expected:x}")
            
                      
            
        #uut._log.info("index=" + str(i) +" value="+ str(hex(value)))


@cocotb.test()
async def memory_test(uut):
    test = Test()
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    uut.i_last.value=0
    uut.i_ready.value=1
    await Timer(100,units="ps")
    await Reset(uut.i_reset,uut.i_clk)
    await Timer(4,units="ns")
    histo = await load_image(uut.i_clk,uut.i_data,uut.i_valid,uut.i_last,uut.o_ready)
    flat_histo=test.Flatten(histo,16)
    await RisingEdge(uut.o_valid)

    await read_histogram(uut.o_histogram_flat,flat_histo)
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