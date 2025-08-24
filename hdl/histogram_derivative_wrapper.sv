`timescale 1ns/100ps
//include "histogram_derivative.sv"



module histogram_derivative_wrapper #(
    parameter TOP = 1, 
    parameter SIZE = 16*256-1

)(
    input i_clk,
    input i_reset,
    input [SIZE:0] i_histogram_flat,
    input i_valid,
    output logic o_ready,
    
    output logic [SIZE:0] o_derivative_flat,
    output logic o_valid,
    input i_ready
);

initial begin 
    if(TOP == 1) begin
        $dumpfile("vars.vcd");
        $dumpvars(0,histogram_derivative_wrapper);
    end
end



enum {s_normal=0, s_skid=1} state;

logic [SIZE:0] histogram_flat;
logic [SIZE:0] skid_buffer_flat;
logic [SIZE:0] histogram_derivative_data_flat;
logic valid;  



histogram_derivative #(.TOP (0)) u_calculate_derivative (
              
    .i_histogram_flat (histogram_flat),
    .o_derivative_flat (histogram_derivative_data_flat)
);


 always_ff @(posedge(i_clk)) begin : data_pipe_with_skid_buffer
    if(i_reset) begin 
        o_derivative_flat <= 0;
        o_valid <= 0;
        o_ready <= 0;
        state <= s_normal;
        valid <= 0;
    end else begin

        o_ready <= i_ready;

        case(state)
            s_normal : begin
                histogram_flat <= i_histogram_flat;
                o_derivative_flat <= histogram_derivative_data_flat;
                valid <= i_valid;
                o_valid <= valid;
                
                if(i_ready == 0 & o_valid==1)begin  
                    o_derivative_flat <= o_derivative_flat;
                    skid_buffer_flat <= histogram_derivative_data_flat;
                    o_valid <= o_valid; 
                    state <= s_skid;
                end
           
            end //state
            s_skid : begin 
                if(i_ready) begin
                    o_derivative_flat <= skid_buffer_flat;
                    o_valid <= 1;
                    state <= s_normal;
                end
            end// state  
        endcase 
    end 

 end  



    
endmodule