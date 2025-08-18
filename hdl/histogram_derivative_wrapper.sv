`timescale 1ns/100ps
`include "histogram_derivative.sv"

module moduleName (
    input i_clk,
    input i_reset,
    input [15:0] i_histogram [255:0],
    input i_valid,
    output logic o_ready,
    
    output logic [15:0] o_derivative [255:0],
    output logic o_valid,
    input i_ready
);


enum {s_normal=0, s_skid=1} state;

logic [15:0] histogram [255:0];
logic [15:0] skid_buffer [255:0];
logic [15:0] histogram_derivative_data [255:0];
logic valid; 

histogram_derivative calculate_derivative (
    .i_histogram(histogram),
    .o_derivative(histogram_derivative_data)
);


 always_ff @(posedge(i_clk)) begin : data_pipe_with_skid_buffer
    if(i_reset) begin 
        o_ready <= 0;
        o_valid <= 0;
        o_ready <= i_ready;
        state <= s_normal;
    end else begin
        case(state)
            s_normal : begin
                for (int i = 0; i<256; i++) begin  
                    histogram[i] <= i_histogram[i];
                    o_derivative[i] <= histogram_derivative_data[i];
                end // for loop
                valid <= i_valid;
                o_valid <= valid;
                
                if(i_ready == 0 & o_valid==1)begin
                    for (int i = 0; i<256; i++) begin  
                        o_derivative[i] <= o_derivative[i];
                        skid_buffer[i] <= histogram_derivative_data[i];
                    end // end for
                     o_valid <= o_valid; 
                     state <= s_skid;
                end// end if 
           
            end //state
            s_skid : begin 
                if(i_ready) begin
                    for (int i = 0; i<256; i++) o_derivative[i] <= skid_buffer[i];
                    o_valid <= 1;
                    state <= s_normal;
                end
            end// state  
        endcase 
    end 

 end  



    
endmodule