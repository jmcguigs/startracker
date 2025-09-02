from cocotb.triggers import RisingEdge
from cocotb.clock import Clock, Timer
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



class AXIS_Test:
    def __init__(self,i_clk,i_reset,i_data,i_valid,o_ready,o_data,o_valid,i_ready):
        self.clk = i_clk
        self.reset = i_reset
        self.i_data = i_data
        self.i_valid = i_valid
        self.o_ready = o_ready
        self.o_data = o_data
        self.o_valid = o_valid 
        self.i_ready = i_ready 

    async def Reset(self,cycles=4):
        self.i_valid.value = 0
        self.i_ready.value = 0
        self.reset.value = 1
        for i in range(cycles):
            await RisingEdge(self.clk)
        self.reset.value = 0

    async def Send(self,data):
        sent = False
        #print(f"trying to send {data:x}")
        while(sent == False):
            await Timer(100, units="ps")
            self.i_data.value = data
            self.i_valid.value = 1
            if(self.o_ready.value):
                await RisingEdge(self.clk)
                #print("ready to send data")
                sent = True
            else:
                await RisingEdge(self.clk)
        self.i_valid.value = 0
        self.i_data.value = 0
        await Timer(100, units="ps")
        
                
            
        


    async def Recieve(self,
                      expected_reads=1,
                      random_ready=False,
                      ready_percent=75):
        
        collected_data = []
        
        for i in range(expected_reads):
            if(random_ready):
                ready_set = False
                while(not ready_set):
                    if(random.randint(0,99) < ready_percent):
                        #print(f"ready set in read {i}")
                        self.i_ready.value = 1
                        ready_set = True
                    else:
                        self.i_ready.value = 0
                        #print(f"not set ready in {i}")
                        await self.Clkwait()
                
                for i in range(40):
                    if(self.o_valid.value==0):
                        #print(f"not valid {i}")
                        await self.Clkwait()
                    else: 
                        break
            else:
                self.i_ready.value = 1
                
                for i in range(40):
                    if(self.o_valid.value==0):
                        #print(f"not valid {i}")
                        await self.Clkwait()
                    else: 
                        break
                
            collected_data.append(self.o_data.value)
            await self.Clkwait()
            self.i_ready.value = 0
        return collected_data
    
    def Flatten(self,array,reg_size_in_bits):
        flat = 0
        for i,vector in enumerate(array):
            if(vector<0):
                flat += (vector + 2**(reg_size_in_bits)) * 2**(reg_size_in_bits * i)
            else :
                flat +=  vector * 2**(reg_size_in_bits * i)
        return flat

    async def Clkwait(self,wait=1):
        for i in range(wait):
            await RisingEdge(self.clk)
            await Timer(100,units="ps")
    





