/**
Alex Knowlton
11/1/2024

ideal mac with control signals to add or clear.

Parameters:
    N_X - number of bits in input X and output Z, default 16
    N_W - number of bits in input W (weight input)
    R_X - number of fractional bits in X
    R_W - number of fractional bits in W

Inputs:
    x_i: N_X bits signed fixed point data input.
    w_i: N_W bits signed fixed point weight input
    add_i: control bit to add x_i * w_i to the sum
    clear_i: control bit to clear the sum on the next cycle
    clk_i: input clock
    rstb_i: active low reset

Output:
    sum_o: N_X bits signed fixed point MAC result. for now, assume overflow
    never happens, but will have to deal with it later.
*/

module ideal_mac #(
    parameter N_X = 16,
    parameter N_W = 16,
    parameter R_X = 8,
    parameter R_W = 8,
    parameter N_SUMS = 17
) (
    input logic signed [N_X-1:0] x_i,
    input logic signed [N_W-1:0] w_i,
    input logic add_i,
    input logic clear_i,
    input logic clk_i,
    input logic rstb_i,
    output logic signed [N_X-1:0] sum_o
);

    localparam signed [N_X-1:0] MAX_VALUE = {1'b0, {{N_X-1}{1'b1}}};

    logic signed [$clog2(N_SUMS)+N_X+N_W-1:0] sum_r, sum_n;
    logic signed [N_X-1:0] trimmed_sum;
    logic signed [N_X+N_W-1:0] product;
    logic overflow, underflow;

    // for now, assume overflow is always 0. However, when that's figured out,
    // saturate the output
    assign overflow = 1'b0;
    assign underflow = 1'b0;

    assign product = x_i * w_i;
    assign sum_n = sum_r + product;
    assign trimmed_sum = sum_n[N_X-1+R_W:R_W];
    assign sum_o = overflow  ?  MAX_VALUE :
                   underflow ? ~MAX_VALUE : trimmed_sum;

    always_ff @(posedge clk_i) begin
        if (~rstb_i)
            sum_r <= '0;
        else
            sum_r <= sum_n;
    end

endmodule