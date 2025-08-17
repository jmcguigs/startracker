`timescale 1ns/1ps

module counter (
    input clk,
    input reset,      // Synchronous active-high reset
    output reg [3:0] q);

    always @(posedge clk) begin
        case(reset)
            1'b0: q <= q + 4'b0001;
            default: q <= 4'b0000;
        endcase
    end
endmodule