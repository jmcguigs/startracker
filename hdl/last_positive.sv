module last_positive #(
    parameter TOP = 1
) (
    input i_clk,
    input i_reset,
    output logic o_ready,
    input i_valid, 
    input [256*16-1:0] i_derivative_flat,
    output logic [7:0] o_threshold,
    output logic o_valid
);


    logic [7:0] threshhold_pipe [15:0];
    logic [7:0] threshhold_reg [15:0];
    logic search;
    enum {s_ready=0,s_search=1,s_send=2} state;

    
    intial begin 
        if(TOP == 1) begin
            $dumpfile("vars.vcd");
            $dumpvars(0, threshold_chunk);
        end
    end

    generate 
        genvar i;
        for(i=0; i<16; i = i+1) begin 
            threshold_gen #(0) threshhold(
                .i_histogram_chunk (i_histogram_flat[i*16*8-1:16*i])
                .i_bin_index(i*16)
                .o_threshold (threshhold_reg[i])
            )
        end  
    endgenerate  

    always_ff(i_clk)
    begin 
        if(i_reset)
        begin
            found <= 0;
            o_threshold <= 0;
            o_valid <= 0;
            o_ready <= 0;
            search <= 0;
            state <= 0;

            for(int i = 0; i<16; i++) begin
                threshhold_pipe[i] <= 0;
                threshhold_reg[i] <= 0;
            end
        end else begin

            found <= 0;
            o_threshold <= o_threshold;
            o_valid <= 0;
            o_ready <= 0;
            search <= 0;
            state <= s_ready;

            case(state)
                s_ready: 
                    begin
                        o_ready <= 1;
                        if(i_valid) begin
                            o_ready <= 0;
                            search <= 1;
                            state <= s_search;
                            for(int i = 0; i<16; i++) begin
                                threshhold_pipe[i] <= threshhold_reg[i];   
                            end
                        end 
                    end // end state 
                
                s_search:

                for(int i = 0; i<15; i++) begin
                    threshhold_pipe[i+1] <= threshhold_pipe[i]
                end
                    if( threshhold_pipe[15]> 0) begin
                        o_threshold <= threshhold_pipe[15];
                        state <= s_send
                        o_valid <= 1
                    end
                
                s_send: 
                begin 
                    o_valid <= 1;
                    if(i_ready) begin
                        o_valid <= 0;
                        state <= s_ready;
                    end
                end
            endcase
        end
    end  
endmodule