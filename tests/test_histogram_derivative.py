import os
import sys
from pathlib import Path

import cocotb
from cocotb.clock import Timer
from cocotb.runner import get_runner


FILE_NAME = "histogram_derivative"

@cocotb.test()
async def derivative_zero_test(dut):
    """Test that histogram_derivative.sv computes the derivative correctly"""

    for i in range(256):
        dut.i_histogram[i].value = i

    await Timer(5, units="ns")
    for i in range(256):
        expected_derivative = i - (i - 1) if i > 0 else i
        assert dut.o_derivative[i].value == expected_derivative, (
            f"Derivative at index {i} was incorrect: "
            f"expected {expected_derivative}, got {dut.o_derivative[i].value}"
        )


@cocotb.test()
async def derivative_nonzero_test(dut):
    """Test that histogram_derivative.sv computes the derivative correctly"""

    for i in range(256):
        dut.i_histogram[i].value = i

    await Timer(5, units="ns")
    for i in range(256):
        expected_derivative = i if i == 0 else i - (i - 1)
        assert dut.o_derivative[i].value == expected_derivative, (
            f"Derivative at index {i} was incorrect: "
            f"expected {expected_derivative}, got {dut.o_derivative[i].value}"
        )


@cocotb.test()
async def derivative_negative_test(dut):
    """Test that histogram_derivative.sv computes the derivative correctly"""

    for i in range(256):
        dut.i_histogram[i].value = 255 - i

    await Timer(5, units="ns")
    for i in range(256):
        expected_derivative = -1 * i if i == 0 else -1 * (i - (i - 1))
        assert dut.o_derivative[i].value.signed_integer == expected_derivative, (
            f"Derivative at index {i} was incorrect: "
            f"expected {expected_derivative}, got {dut.o_derivative[i].value}"
        )


def test_histogram_derivative_runner():
    """
    Simulate the histogram derivative module using cocotb.
    """
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "model"))

    sources = [proj_path / "hdl" / f"{FILE_NAME}.sv"]

    build_test_args = []

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "tests"))

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=FILE_NAME,
        always=True,
        build_args=build_test_args
    )
    runner.test(
        hdl_toplevel=FILE_NAME, test_module="test_histogram_derivative", test_args=build_test_args
    )


if __name__ == "__main__":
    test_histogram_derivative_runner()