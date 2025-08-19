from cocotb.triggers import RisingEdge

class Test:
    def __init__(self):
        pass

    async def Reset(self,clk,reset,cycles=4):
        reset.value = 1
        for i in range(cycles):
            await RisingEdge(clk)
        reset.value = 0
