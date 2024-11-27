/**
Alex Knowlton
11/27/2024

Activation function using CORDIC algorithm. uses standard handshake.

Parameters:
    N - number of bits in input/output data
    R - number of fractional bits
    IS_TANH - if true, computes tanh. else, computes sigmoid
    N_ITERATIONS - number of iterations for linear division
*/

module afb #(
    parameter N=16,
    parameter R=12,
    parameter logic IS_TANH=1,
    parameter N_ITERATIONS=12
) (
    input logic signed [N-1:0] data_i, // theta
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    logic signed [N-1:0] data_i_shift;
    logic [2*N-1:0] afb_lo;
    logic valid_lo, ready_lo;
    assign data_i_shift = IS_TANH ? data_i : data_i >>> 1;

    afb_hyperbolic_handshake hyperbolic (
        .data_i(data_i_shift),
        .valid_i,
        .ready_o,

        .data_o(afb_lo),
        .valid_o(valid_lo),
        .yumi_i(ready_lo),

        .clk(clk_i),
        .rst(rstb_i)
    );

    afb_linear_handshake #(
        .N(N),
        .R(R),
        .IS_TANH(IS_TANH),
        .N_ITERATIONS(N_ITERATIONS)
    ) linear (
        .data_i(afb_lo),
        .valid_i(valid_lo),
        .ready_o(ready_lo),

        .data_o,
        .valid_o,
        .yumi_i,
        
        .clk_i,
        .rstb_i
    );

endmodule