/**
Alex Knowlton
11/2/2024

LSTM layer. Has standard handshakes at input and output.

parameters:
    N_X - number of bits in X word
    N_W - number of bits in W word
    R_X - number of fractional bits in X
    R_W - number of fractional bits in W
    INPUT_LENGTH - length of input vector X
    OUTPUT_LENGTH - length of output vector Y
    LAYER_NUMBER - index of the layer in the network, used for memory files
*/

module lstm_layer #(
    parameter N_X=16,
    parameter N_W=8,
    parameter R_X=8,
    parameter R_W=8,
    parameter INPUT_LENGTH=4,
    parameter OUTPUT_LENGTH=3,
    parameter LAYER_NUMBER=6
) (
    input logic [N_X-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [N_X-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    // controller to feed data from input to MAC and select betwen X and H
    lstm_controller #(
        .N_X(N_X),
        .N_W(N_W),
        .R_X(R_X),
        .R_W(R_W),
        .INPUT_LENGTH(INPUT_LENGTH),
        .OUTPUT_LENGTH(OUTPUT_LENGTH),
        .LAYER_NUMBER(LAYER_NUMBER)
    ) (
        .x_data_i(),
        .x_valid_i(),
        .x_ready_o(),

        .h_data_i(),
        .h_valid_i(),
        .h_ready_o(),

        .data_o(),
        .valid_o(),
        .yumi_i(),

        .clk_i,
        .rstb_i
    );

    // H queue to capture previous output
    hidden_state_queue #(
        .LENGTH(OUTPUT_LENGTH),
        .N_X(N_X)
    ) h_queue (
        .data_i(),
        .valid_i(),
        .ready_o(),

        .data_o(),
        .valid_o(),
        .yumi_i(),

        .clk_i,
        .rstb_i
    );

    genvar i;
    generate

        // MAC array communicating with controller
        mac_array_ideal #(
            .N_X(N_X),
            .N_W(N_W),
            .R_X(R_X),
            .R_W(R_W),
            .ARRAY_LENGTH(OUTPUT_LENGTH),
            .N_SUMS(INPUT_LENGTH+OUTPUT_LENGTH+1)
        ) mac_array (
            .data_i(),
            .valid_i(),
            .ready_o(),

            .data_o(),
            .valid_o(),
            .yumi_i(),

            .clk_i,
            .rstb_i
        );
        

        // PISO layers connecting with MAC
        piso #(
            .LAYER_HEIGHT(OUTPUT_LENGTH),
            .WORD_SIZE(N_X)
        ) output_layer (
            .clk_i,
            .reset_i(~rstb_i),

            .ready_o(),
            .valid_i(),
            .data_i(),

            .valid_o(),
            .yumi_i(),
            .data_o()
        );
    endgenerate

    // AFB block connecting to output
    lstm_relu_ideal #(
        .N(N_X)
    ) afb (
        .data_i(),
        .valid_i(),
        .ready_o(),

        .data_o(),
        .valid_o(),
        .yumi_i(),

        .clk_i,
        .rstb_i
    );

endmodule