module last_positive #(
    parameter TOP = 1
) (
    input i_clk,
    input i_reset,
    output logic o_ready,
    input i_valid, 
    input [256*17-1:0] i_derivative_flat,
    output logic [7:0] o_threshold,
    output logic o_valid,
    input i_ready
);

    logic [7:0] threshhold_pipe [31:0];
    logic [7:0] threshhold_reg [31:0];
    logic [7:0] mult_lookup [31:0];
    enum {s_ready=0,s_search=1,s_send=2} state;
    logic [7:0] tp0, tp1, tp2, tp3;

    
    assign tp0 = threshhold_reg[31];
    assign tp1 = threshhold_reg[31];
    assign tp2 = threshhold_reg[30];
    assign tp3 = threshhold_reg[29];


    genvar j;
    for( j = 0; j<32; j++)
    begin
        assign mult_lookup[j] = j * 8;
    end

    
    initial begin 
        if(TOP == 1) begin
            $dumpfile("vars.vcd");
            $dumpvars(0, last_positive);
        end
    end

    generate 
        genvar i;
        for(i=0; i<32; i = i+1) begin 
            
            
            threshold_chunk  #(.TOP (0)) threshold_gen (
                .i_histogram_chunk (i_derivative_flat[(i+1)*17*8-1 : 17*8*i]),
                .i_bin_index (mult_lookup[i]),
                .o_threshold (threshhold_reg[i])
            );
        end  
    endgenerate  

    always_ff@(posedge(i_clk))
    begin 
        if(i_reset)
        begin
            o_threshold <= 0;
            o_valid <= 0;
            o_ready <= 0;
            state <= s_ready;
            o_threshold <= 0;

            for(int k = 0; k<32; k++) begin
                threshhold_pipe[k] <= 0;
            end
        end else begin

            o_threshold <= o_threshold;
            o_valid <= 0;
            o_ready <= 0;
            state <= state;

            case(state)
                s_ready: 
                    begin
                        o_ready <= 1;
                        if(i_valid && o_ready) begin
                            o_ready <= 0;
                            state <= s_search;
                            for(int i = 0; i<32; i++) begin
                                threshhold_pipe[i] <= threshhold_reg[i];   
                            end
                        end 
                    end // end state 
                
                s_search:
                begin
                    for(int i = 0; i<32; i++) begin
                        threshhold_pipe[i+1] <= threshhold_pipe[i];
                    end
                    if( threshhold_pipe[31]> 0) begin
                        o_threshold <= threshhold_pipe[31];
                        state <= s_send;
                        o_valid <= 1;
                    end
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