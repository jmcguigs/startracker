`timescale 1ns/100ps

module threshold_chunk #(
    parameter TOP = 1
) (
    input [8*17-1:0] i_histogram_chunk,
    input [7:0] i_bin_index,
    output logic [7:0] o_threshold
);

    initial begin 
        if(TOP == 1) begin
            $dumpfile("vars.vcd");
            $dumpvars(0, threshold_chunk);
        end
    end

    // give most significant index priority
    // input is a chunk of 8 bins (17 bits per bin)
    // output is the index of the first positive bin in that chunk - absolute index using i_bin_index
    
    logic [7:0] threshhold [7:0];
    logic signed [16:0] histogram_chunk[7:0];
    
    genvar i;
    for ( i = 0; i<8; i++) begin 
        assign histogram_chunk[i] = i_histogram_chunk[((i+1)*17)-1 : i*17];
    end



    assign o_threshold = threshhold[7];


    
    always_comb begin // sentinel value if no positive bin is found
        for (int i = 0; i <8; i++) begin
            // check if the LSB of the bin is not set (i.e., bin is positive)
            if(i==0) begin 
                if (histogram_chunk[i] > 0) threshhold[i] = i_bin_index + i;   
                else threshhold[i] = 0 + i_bin_index;
            end else begin 
                if (histogram_chunk[i] > 0) threshhold[i] = i_bin_index + i;
                else threshhold[i] = threshhold[i-1];
            end
        end
    end



endmodule