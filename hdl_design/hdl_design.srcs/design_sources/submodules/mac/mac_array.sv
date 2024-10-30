/**
Alex Knowlton
10/29/24

Ideal MAC array. Delays one cycle between each handshake to test robustness
of interfaces in other layer components, but computes sum of products. Data
input must be formatted as a packed array as follows:
{[N_X-1:0][[ARRAY_LENGTH-1:0][N_W-1:0]]}
 | X in   | packed weight array, N_W bits each |
*/

module mac_array #(
    parameter N_X=16,
    parameter N_W=16,
    parameter R_X=8,
    parameter R_W=8,
    parameter ARRAY_LENGTH=16,
    parameter N_SUMS=17
) (
    input logic valid_i,
    output logic ready_o,
    input logic [(N_X+ARRAY_LENGTH*N_W)-1:0] data_i,

    output logic [ARRAY_LENGTH-1:0][N_X-1:0] data_o,
    input logic yumi_i,
    output logic valid_o,

    input logic clk_i,
    input logic rstb_i
);

endmodule