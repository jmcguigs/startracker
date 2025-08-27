from cocotb.triggers import RisingEdge
import random

class Test:
    def __init__(self):
        pass

    async def Reset(self,clk,reset,cycles=4):
        reset.value = 1
        for i in range(cycles):
            await RisingEdge(clk)
        reset.value = 0

    async def Axi4_Stream_Last_If(self, clk, data, valid, ready, last, pattern):
        
        for i, frame in pattern:
            if(i == (len(pattern)-1)):
                last.value = 1
            else:
                last.value = 0

            valid.value = 1
            data.value = frame
            
            if(ready.value != 1):
                while(ready.value != 1):
                    await RisingEdge(clk)
            else:
                await RisingEdge(clk)

    async def Axi4_Stream_If(self, clk, data, valid, ready, pattern):
        
        for i, frame in pattern:
            
            valid.value = 1
            data.value = frame
            
            if(ready.value != 1):
                while(ready.value != 1):
                    await RisingEdge(clk)
            else:
                await RisingEdge(clk)

    async def Axi4_Stream_Reciever(self, 
                                   clk, 
                                   ready, 
                                   valid, 
                                   data,
                                   random_ready, 
                                   ready_percentage=75,
                                   expected_reads=1):
        collected_data = []
        for i in range(expected_reads):
            # wait until valid data recieved
            while (True):
                # set ready  
                if(random_ready == True):
                    if(random.randint(0,99) < ready_percentage):
                        ready.value = 1
                    else:
                        ready.value = 0
                else:
                    ready.value = 0
                # valid read condition 
                if(valid.value==1 and ready.value==1):
                    collected_data.append(data.value)
                    await RisingEdge(clk)
                    break
       
        return collected_data
    
    def Flatten(self,array,reg_size_in_bits):
        flat = 0
        for i,vector in enumerate(array):
            if(vector<0):
                flat += (vector + 2**(reg_size_in_bits)) * 2**(reg_size_in_bits * i)
            else :
                flat +=  vector * 2**(reg_size_in_bits * i)
        return flat




                


