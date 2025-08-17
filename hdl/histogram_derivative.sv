`timescale 1ns/1ps

module histogram_derivative(
    input logic [7:0][15:0] i_histogram,
    output logic [7:0][15:0] o_derivative
);

    // take the discrete derivative of the histogram

    always_comb begin
        for (int i = 0; i < 256; i++) begin
            if (i < 255) begin
                o_derivative[i] = i_histogram[i] - i_histogram[i - 1]; // Calculate derivative for elements 1 to 254
            end else begin
                o_derivative[i] = 0; // Last element has no next element to subtract from
            end
        end
    end

endmodule