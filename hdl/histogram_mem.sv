`timescale 1ns/1ps

module histogram_mem(
    input i_clk,
    input i_reset,
    input i_valid,
    input [7:0] i_data,
    input i_last,
    output logic o_ready,

    output logic [7:0][15:0] o_histogram,
    output logic o_valid,
    input  i_ready

);

enum {s_initial = 0, s_request = 1, s_recieve=2, s_done=3 , s_clear =4} state;
intager i;

    always_ff @(i_clk) begin : 
        if(i_reset) begin
            state <= s_initial; 
            o_histogram <= 0;
            o_valid <= 0;
            o_ready <= 0;
            for (i=0 i<256; i=i+1) o_histogram[i] <= 0;
        end else begin 

            o_ready <= 0;
            o_valid <= 0;

            case(state)
                s_initial : begin
                    o_ready <= 1;
                    if(i_valid) begin
                        o_histogram[i_data] <= o_histogram[i_data] + 1;
                        if(i_last) begin 
                            state <= s_done;
                            o_ready <= 0;
                        end
                    end
                end// state

                s_done : begin 
                    o_valid <= 1;
                    if(i_ready) begin 
                        state <= s_clear;
                    end
                end// state
                s_clear : begin
                    for (i=0 i<256; i=i+1) o_histogram[i] <= 0;
                    state <= s_initial;
                end
            endcase 
        end     
    end
endmodule