/**
Alex Knowlton
10/29/2924

Fully-connected layer. Takes input beginning from X_0 up to X_n-1, where n
is the size of the input vector. Computes Ax + b, where A is a weight matrix,
x is a vector, and b is a bias vector. A and b are stored in memory.

Parameters:
    N_X: number of bits per word in input vector X
    N_W: number of bits per word in weight/bias memory
    R_X: number of fractional bits in X
    R_W: number of fractional bits in W
    LAYER_NUMBER: layer number in the network, used for .mif indexing
    INPUT_LENGTH: length of input vector X
    OUTPUT_LENGTH: length of output vector Y
*/

module fc_layer #(
    parameter N_X = 16,
    parameter N_W = 16,
    parameter R_X = 12,
    parameter R_W = 12,
    parameter LAYER_NUMBER = 4,
    parameter INPUT_LENGTH = 5,
    parameter OUTPUT_LENGTH = 3
) (
    input logic clk_i,
    input logic rstb_i,
    
    input logic [N_X-1:0] data_i,
    input logic valid_i,
    output logic ready_o,
    
    output logic [N_X-1:0] data_o,
    output logic valid_o,
    input logic yumi_i
);

    // instantiate controller to handle data from previous layer to MAC
    logic ctrl_valid_lo, ctrl_yumi_li;
    logic [(N_X+OUTPUT_LENGTH*N_W)-1:0] ctrl_data_lo;

    fc_controller #(
        .LAYER_NUMBER(LAYER_NUMBER),
        .N_INPUTS(INPUT_LENGTH),
        .N_OUTPUTS(OUTPUT_LENGTH),
        .N_BITS_MEM(N_W),
        .N_BITS_DATA(N_X)
    ) control (
        .clk_i,
        .rstb_i,

        .valid_i,
        .ready_o,
        .data_i,

        .valid_o(ctrl_valid_lo),
        .yumi_i(ctrl_yumi_li),
        .data_o(ctrl_data_lo)
    );

    // instantiate MAC array
    logic mac_valid_lo, mac_yumi_li;
    logic [OUTPUT_LENGTH-1:0][N_X-1:0] mac_data_lo;

    cordic_mac_array #(
        .WIDTH(N_X),
        .FRACTIONAL_BITS(R_X),
        .N_INPUTS(INPUT_LENGTH+1),
        .ARRAY_LENGTH(OUTPUT_LENGTH)
    ) mac (
        .clk_i,
        .rstb_i,
        .valid_i(ctrl_valid_lo),
        .ready_o(ctrl_yumi_li),
        .data_i(ctrl_data_lo),
        .valid_o(mac_valid_lo),
        .yumi_i(mac_yumi_li),
        .data_o(mac_data_lo)
    );

    // instantiate PISO layer to connect to output
    piso #(
        .LAYER_HEIGHT(OUTPUT_LENGTH),
        .WORD_SIZE(N_X)
    ) output_layer (
        .clk_i,
        .reset_i(~rstb_i),

        .ready_o(mac_yumi_li),
        .valid_i(mac_valid_lo),
        .data_i(mac_data_lo),

        .valid_o,
        .yumi_i,
        .data_o
    );

endmodule
