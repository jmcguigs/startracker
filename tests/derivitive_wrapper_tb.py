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
VERILOG_FILE_NAMES.append("histogram_derivative.sv")
VERILOG_FILE_NAMES.append("histogram_derivative_wrapper.sv")


TOP_MODULE_NAME ="histogram_derivative_wrapper"
PYTHON_FILE_NAME="derivitive_wrapper_tb"



def pattern_gen(repeats, style="random"):
    values =256*[0]
    match style:
        case "ramp":
            for j in range(repeats):
                for i in range(256):
                    values[i] += i
        case "uniform":
            for j in range(repeats):
                for i in range(256):
                    values[i] += 1
        case "random":
            for i in range(256):
                values[i]=random.randint(0,500)
        case _:
            assert 1==0, (f"pattern {style} is not a valid input in pattern gen")
    return values

def calculate_deriviative(values):
    dy = []
    for i in range(len(values)):
        if(i == 0):
            dy.append(0)
        else:
            dy.append(values[i] - values[i-1])
    return dy


async def Axi4_Stream_If_Histogram(clk, data, valid, ready, pattern):
        valid.value = 1     
        data.value=pattern
        await RisingEdge(ready)
        await RisingEdge(clk)
        valid.value = 0
        

async def Axi4_Stream_Reciever_Derriviative(clk,  
                                            ready, 
                                            valid, 
                                            data,
                                            random_ready, 
                                            ready_percentage=75,
                                            expected_reads=1):
        collected_data = []
        # wait until valid data recieved
        kl = 0
        while (True):
            # set ready  
            if(random_ready == True):
                if(random.randint(0,99) < ready_percentage):
                    ready.value = 1
                else:
                    ready.value = 0
            else:
                ready.value = 1
            
            # valid read condition 
            kl += 1
            #print(f"k is {kl}")
            if (kl==100): break
            
            if(valid.value==1 and ready.value==1):
                collected_data.append(data.value)
                await RisingEdge(clk)
                #print(f"data is {collected_data}")
                break
            else:
                await RisingEdge(clk)
        if(kl==100): pass #print("broken")
        return collected_data

# test 1 
@cocotb.test()
async def flat(uut):

    uut.i_histogram_flat.value = 0
    uut.i_valid.value=0
    uut.i_ready.value=0
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    test = Test()
    await test.Reset(uut.i_clk, uut.i_reset)
    input_data = pattern_gen(2,"uniform")
    my_deriv=calculate_deriviative(input_data)
    excpected = test.Flatten(calculate_deriviative(input_data),17)
    await RisingEdge(uut.i_clk)
    cocotb.start_soon(Axi4_Stream_If_Histogram(uut.i_clk, uut.i_histogram_flat, uut.i_valid, uut.o_ready, test.Flatten(input_data,16)))
    recv = await Axi4_Stream_Reciever_Derriviative(uut.i_clk,uut.i_ready,uut.o_valid,uut.o_derivative_flat,True,10,1)
    await RisingEdge(uut.i_clk)
    recieved = int(recv[0])
    assert  excpected ==  recieved, (f"\nexpected {excpected:x} \n\nrecieved {recieved:x}")
    await Timer(10*2,units="ns")


# test 2
@cocotb.test()
async def ramp(uut):

    uut.i_histogram_flat.value = 0
    uut.i_valid.value=0
    uut.i_ready.value=0
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    test = Test()
    await test.Reset(uut.i_clk, uut.i_reset)
    input_data = pattern_gen(2,"ramp")
    my_deriv=calculate_deriviative(input_data)
    excpected = test.Flatten(calculate_deriviative(input_data),17)
    await RisingEdge(uut.i_clk)
    cocotb.start_soon(Axi4_Stream_If_Histogram(uut.i_clk, uut.i_histogram_flat, uut.i_valid, uut.o_ready, test.Flatten(input_data,16)))
    recv = await Axi4_Stream_Reciever_Derriviative(uut.i_clk,uut.i_ready,uut.o_valid,uut.o_derivative_flat,True,10,1)
    await RisingEdge(uut.i_clk)
    recieved = int(recv[0])
    assert  excpected ==  recieved, (f"\nexpected {excpected:x} \n\nrecieved {recieved:x}")
    await Timer(10*2,units="ns")


@cocotb.test()
async def random_input(uut):

    uut.i_histogram_flat.value = 0
    uut.i_valid.value=0
    uut.i_ready.value=0
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    test = Test()
    await test.Reset(uut.i_clk, uut.i_reset)
    input_data = pattern_gen(2,"ramp")
    my_deriv=calculate_deriviative(input_data)
    excpected = test.Flatten(calculate_deriviative(input_data),17)
    await RisingEdge(uut.i_clk)
    cocotb.start_soon(Axi4_Stream_If_Histogram(uut.i_clk, uut.i_histogram_flat, uut.i_valid, uut.o_ready, test.Flatten(input_data,16)))
    recv = await Axi4_Stream_Reciever_Derriviative(uut.i_clk,uut.i_ready,uut.o_valid,uut.o_derivative_flat,True,10,1)
    await RisingEdge(uut.i_clk)
    recieved = int(recv[0])
    assert  excpected ==  recieved, (f"\nexpected {excpected:x} \n\nrecieved {recieved:x}")
    await Timer(10*2,units="ns")

    


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