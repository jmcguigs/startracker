import os
import sys
from pathlib import Path


import random



import cocotb
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.binary import BinaryValue

from utils.test_common import Test



VERILOG_FILE_NAMES = []
VERILOG_FILE_NAMES.append("threshold_chunk.sv")



TOP_MODULE_NAME ="threshold_chunk"
PYTHON_FILE_NAME="threshold_chunk_tb"


def random_number_gen(low,high):
    der = []
    for val in range (8):
        der.append( random.randint(low,high) )
    print(der)
    return der

def expected_gen(array,base):
    last_pos = 0
    for i,value in enumerate(array):
        if value > 0:
            last_pos = i
    return last_pos + base




@cocotb.test()
async def random_test_base(uut):
    test = Test()
    uut.i_bin_index.value = 0
    for i in range(10):
        input_array=random_number_gen(-20,7)
        expected = expected_gen(input_array,0)
        input = test.Flatten(input_array,17)
        uut.i_histogram_chunk.value = input
        await Timer(2,units="ns")
        actual = int(uut.o_threshold.value)
        assert actual == expected, (f"actual = {actual}, expected = {expected}")


@cocotb.test()
async def random_test_top(uut):
    test = Test()
    uut.i_bin_index.value = 17*7
    for i in range(10):
        input_array=random_number_gen(-20,7)
        expected = expected_gen(input_array,17*7)
        input = test.Flatten(input_array,17)
        uut.i_histogram_chunk.value = input
        await Timer(2,units="ns")
        actual = int(uut.o_threshold.value)
        assert actual == expected, (f"actual = {actual}, expected = {expected}")
    


def test_wrapper_runner():
    """
    Simulate the 4-bit binary counter using cocotb and the specified HDL language.
    """
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable
    sources = []
    for VERILOG_FILE_NAME in VERILOG_FILE_NAMES:
         sources.append(proj_path / "hdl" / VERILOG_FILE_NAME)
    
        
    #sources = ([proj_path / "hdl" / VERILOG_FILE_NAMES[0] , proj_path / "hdl" / VERILOG_FILE_NAMES[1]])

    #sources = ([proj_path / "hdl" / VERILOG_FILE_NAME])

    build_test_args = []

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=TOP_MODULE_NAME,
        always=True,
        build_args=build_test_args
    )
    runner.test(
        hdl_toplevel=TOP_MODULE_NAME, test_module=PYTHON_FILE_NAME, test_args=build_test_args
    )


if __name__ == "__main__":
    test_wrapper_runner()