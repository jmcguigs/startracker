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
from utils.test_common import AXIS_Test



VERILOG_FILE_NAMES = []
VERILOG_FILE_NAMES.append("threshold_chunk.sv")
VERILOG_FILE_NAMES.append("last_positive.sv")


TOP_MODULE_NAME ="last_positive"
PYTHON_FILE_NAME="last_positive_tb"


def random_number_gen(low,high):
    der = []
    for val in range (256):
        der.append( random.randint(low,high) )
    #print(der)
    return der

def expected_gen(array,base):
    last_pos = 0
    for i,value in enumerate(array):
        if value > 0:
            last_pos = i
    return last_pos + base

async def multi_write(test :AXIS_Test, write_array):
    for i,input in enumerate(write_array):
        await test.Send(test.Flatten(input,17))
        #print(f"send {i}")


@cocotb.test()
async def always_ready_signle_write(uut):
    test = AXIS_Test(i_clk = uut.i_clk,
                     i_reset = uut.i_reset,
                     i_data = uut.i_derivative_flat,
                     i_valid = uut.i_valid,
                     o_ready = uut.o_ready,
                     o_data = uut.o_threshold,
                     o_valid = uut.o_valid,
                     i_ready = uut.i_ready)
    
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    await Timer(2,units="ns")
    await test.Reset()
    await test.Clkwait(2)
    input_array = random_number_gen(-200,5)
    expected = expected_gen(input_array,0)
    cocotb.start_soon(test.Send(test.Flatten(input_array,17)))
    actual_array = await test.Recieve(1,False)
    await test.Clkwait(2)
    #print(actual_array)
    actual = int(actual_array[0])
    assert actual == expected , (f"actaul = {actual}, expected = {expected}")




@cocotb.test()
async def random_ready_signle_write(uut):
    test = AXIS_Test(i_clk = uut.i_clk,
                     i_reset = uut.i_reset,
                     i_data = uut.i_derivative_flat,
                     i_valid = uut.i_valid,
                     o_ready = uut.o_ready,
                     o_data = uut.o_threshold,
                     o_valid = uut.o_valid,
                     i_ready = uut.i_ready)
    
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    await Timer(2,units="ns")
    await test.Reset()
    await test.Clkwait(2)
    input_array = random_number_gen(-200,5)
    expected = expected_gen(input_array,0)
    cocotb.start_soon(test.Send(test.Flatten(input_array,17)))
    actual_array = await test.Recieve(1,True,5)
    await test.Clkwait(2)
    #print(actual_array)
    actual = int(actual_array[0])
    assert actual == expected , (f"actaul = {actual}, expected = {expected}")


@cocotb.test()
async def random_ready_multi_write(uut):
    writes = 7
    test = AXIS_Test(i_clk = uut.i_clk,
                     i_reset = uut.i_reset,
                     i_data = uut.i_derivative_flat,
                     i_valid = uut.i_valid,
                     o_ready = uut.o_ready,
                     o_data = uut.o_threshold,
                     o_valid = uut.o_valid,
                     i_ready = uut.i_ready)
    
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    await Timer(2,units="ns")
    await test.Reset()
    await test.Clkwait(2)
    expected_list = []
    input_array_list = []
    for i in range(writes):
        input_array = random_number_gen(-200,writes)
        input_array_list.append(input_array)
        expected_list.append(expected_gen(input_array,0))
    cocotb.start_soon(multi_write(test,input_array_list))
    actual_array = await test.Recieve(writes,True,10)
    await test.Clkwait(2)
    #print(actual_array)
    for i, expected in enumerate(expected_list):
        
        actual = int(actual_array[i])
        print(f"actaul = {actual}, expected = {expected} in send {i}")
        assert actual == expected , (f"actaul = {actual}, expected = {expected} in send {i}")



    


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