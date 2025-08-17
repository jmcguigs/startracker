import os
import sys
import random
from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock, Timer
from cocotb.runner import get_runner



@cocotb.test()
async def counter_basic_test(dut):
    """Test that counter.sv does in fact count"""

    # Set initial output value to 0 (as if reset the previous cycle)
    dut.q.value = 0
    dut.reset.value = 0  # Ensure reset is low

    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    expected_val = 1  # one posedge after start
    for i in range(15):
        await RisingEdge(dut.clk)
        await Timer(5, units="ns")
        assert dut.q.value == expected_val, f"output q was incorrect on the {i}th cycle"
        expected_val += 1  # Save random value for next RisingEdge

    # Check the final input on the next clock
    expected_val = 0  # After 15, it should wrap around to 0
    await RisingEdge(dut.clk)
    await Timer(5, units="ns")
    assert dut.q.value == expected_val, "output q was incorrect on the last cycle"


@cocotb.test()
async def counter_reset_test(dut):
    """Test that counter.sv does in fact reset"""

    # Set initial output value to 0 (as if reset the previous cycle)
    dut.q.value = 0
    dut.reset.value = 0

    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    ticks_to_reset = random.randint(1, 10)  # Random number of ticks before reset

    for i in range(ticks_to_reset):
        await RisingEdge(dut.clk)
        await Timer(5, units="ns")
        assert dut.q.value == i + 1, f"output q was incorrect on the {i}th cycle"

    # Now set reset high and check that output is 0
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    await Timer(5, units="ns")
    assert dut.q.value == 0, "output q was not 0 after reset"


def test_counter_runner():
    """
    Simulate the 4-bit binary counter using cocotb and the specified HDL language.
    """
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "model"))

    if hdl_toplevel_lang == "verilog":
        sources = [proj_path / "hdl" / "counter.sv"]
    else:
        sources = [proj_path / "hdl" / "counter.vhdl"]

    build_test_args = []

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="counter",
        always=True,
        build_args=build_test_args
    )
    runner.test(
        hdl_toplevel="counter", test_module="test_counter", test_args=build_test_args
    )


if __name__ == "__main__":
    test_counter_runner()