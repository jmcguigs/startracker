`timescale 1ns/100ps

module histogram_derivative #(
    parameter TOP = 1
)(
    input [256*16-1:0] i_histogram_flat,
    output logic [256*16-1:0] o_derivative_flat
);

    logic [15:0] i_histogram [255:0];
    logic [15:0] o_derivative [255:0];



    initial begin 
        if(TOP == 1)
        begin
            $dumpfile("vars.vcd");
            $dumpvars(0,histogram_derivative);
        end
    end
    // take the discrete derivative of the histogram
    genvar j;
    for(j = 0; j<256; j = j + 1) begin 
        assign  i_histogram[j] = i_histogram_flat[(16*j+15) : j*16];
        assign  o_derivative_flat[(16*j) +15 : j*16] = o_derivative[j];
    end 
    always_comb begin
        
        for (int i = 0; i < 256; i++) begin
            if (i == 0) begin
                o_derivative[i] = 0;
            end else begin
                o_derivative[i] = i_histogram[i] - i_histogram[i - 1];
            end
        end
    end

endmodule