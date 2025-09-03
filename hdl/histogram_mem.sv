`timescale 1ns/100ps

module histogram_mem #(parameter TOP = 1)(
    input i_clk,
    input i_reset,
    input i_valid,
    input [7:0] i_data,
    input i_last,
    output logic o_ready,

    output logic [256*16-1:0] o_histogram_flat,
    output logic o_valid,
    input  i_ready
);

initial begin 
    if(TOP) begin
        $dumpfile("vars.vcd");
        $dumpvars(0,histogram_mem);
    end
end

logic [15:0] o_histogram [255:0];

logic [15:0] tp1,tp2,tp3,tp4; 

assign tp1 = o_histogram[0];
assign tp2 = o_histogram_flat[15:0];
assign tp3 = o_histogram_flat[16*255+15:255*16];
assign tp4 = o_histogram[255];


genvar j;
for (j = 0; j<256; j = j + 1) begin
    assign o_histogram_flat[(j*16)+15:j*16] = o_histogram[j];
end





enum {s_initial = 0, s_recieve = 1, s_done = 3 ,s_clear = 4} state;
integer i;

    always_ff @(posedge(i_clk)) begin
        if(i_reset) begin
            state <= s_initial; 
            o_valid <= 0;
            o_ready <= 0;
            for (i=0; i<256; i=i+1) o_histogram[i] <= 0;
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
                    for (i=0; i<256; i=i+1) o_histogram[i] <= 0;
                    state <= s_initial;
                end
            endcase 
        end     
    end
endmodule