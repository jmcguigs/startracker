`timescale 1ns/100ps

module threshold #(
    parameter TOP = 1
) (
    input [8*16-1:0] i_histogram_chunk,
    input [7:0] i_bin_index,
    output logic [7:0] o_threshold
);

    intial begin 
        if(TOP == 1) begin
            $dumpfile("vars.vcd");
            $dumpvars(0, threshold);
        end
    end

    // find the first bin (starting from the right) that is positive
    // input is a chunk of 8 bins (16 bits per bin)
    // output is the index of the first positive bin in that chunk - absolute index using i_bin_index
    always_comb begin
        o_threshold = 8'h00; // sentinel value if no positive bin is found
        for (int i = 7; i >= 0; i--) begin
            // check if the LSB of the bin is not set (i.e., bin is positive)
            if (i_histogram_chunk[((i + 1) * 16) - 1] == 1'b0) begin
                o_threshold = i_bin_index + i;
            end
        end
    end
endmodule