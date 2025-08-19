import os
import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner

from utils.test_common import Test



VERILOG_FILE_NAMES = []
VERILOG_FILE_NAMES.append("histogram_derivative.sv")
VERILOG_FILE_NAMES.append("histogram_derivative_wrapper.sv")



TOP_MODULE_NAME ="histogram_derivative_wrapper"
PYTHON_FILE_NAME="derivitive_wrapper_tb"


@cocotb.test()
async def memory_test(uut):
    clock = Clock(uut.i_clk, 2, units="ns")
    cocotb.start_soon(clock.start(start_high=True))
    test = Test()
    await test.Reset(uut.i_clk, uut.i_reset)

    await Timer(2,units="ns")
    


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