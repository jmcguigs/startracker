`timescale 1ns/1ps

module histogram_derivative(
    input logic [15:0] i_histogram [0:255],
    output logic [15:0] o_derivative [0:255]
);

    // take the discrete derivative of the histogram

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