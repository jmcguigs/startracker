module moduleName #(
    parameter TOP = 1
) (
    input i_clk,
    input i_reset,
    input [256*16-1:0] i_derivative_flat,
    output logic [7:0] o_threshold,
    output logic o_valid
);


logic [7:0] threshhold_pipe [15:0]
logic found;


generate 
    genvar i;
    for(i=0; i<16; i = i+1) begin 
        threshold_gen #(0) threshhold(
            .i_histogram_chunk (i_histogram_flat[i*16*8-1:16*i])
            .i_bin_index(i*16)
            .o_threshold (threshhold_pipe[i])
        )
    end 

    always_ff(i_clk)
    begin 
        if(i_reset)
        {
            found <= 0;
            o_threshold <= 0;

            for(int i = 0; i<16; i++) begin
                threshhold_pipe[i] <= 0
            end
        }

        for(int i = 0; i<15; i++) begin
            threshhold_pipe[i+1] <= threshhold_pipe[i]
        end

        if(threshhold_pipe[15]>0 && found ==0 ) begin
            o_threshold <= threshhold_pipe[15]
            found=1;
        end  

    end 




endgenerate  






    
endmodule