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
    parameter N_W=16,
    parameter R_X=12,
    parameter R_W=12,
    parameter INPUT_LENGTH=11,
    parameter OUTPUT_LENGTH=4,
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
    logic h_ready_lo, h_valid_lo, lstm_valid_lo;
    logic [3:0] mac_ready_lo, mac_valid_lo, piso_valid_lo, piso_ready_lo;
    logic relu_ready_lo;
    logic [N_X-1:0] h_data_lo, lstm_data_lo;
    logic [3:0][OUTPUT_LENGTH-1:0][N_W-1:0] lstm_mem_lo;
    logic [3:0][OUTPUT_LENGTH-1:0][N_X-1:0] mac_data_lo;
    logic [3:0][N_X-1:0] piso_data_lo;
    logic [(N_X+4*OUTPUT_LENGTH*N_W)-1:0] lstm_data_mem_lo;
    assign lstm_data_lo = lstm_data_mem_lo[(N_X+4*OUTPUT_LENGTH*N_W)-1:4*OUTPUT_LENGTH*N_W];
    assign lstm_mem_lo = lstm_data_mem_lo[4*OUTPUT_LENGTH*N_W-1:0];

    // logic for layer output
    logic queue_ready_lo, relu_valid_lo;
    logic output_handshake;
    assign output_handshake = yumi_i && valid_o;
    assign valid_o = relu_valid_lo && queue_ready_lo;

    lstm_controller #(
        .N_X(N_X),
        .N_W(N_W),
        .R_X(R_X),
        .R_W(R_W),
        .INPUT_LENGTH(INPUT_LENGTH),
        .OUTPUT_LENGTH(OUTPUT_LENGTH),
        .LAYER_NUMBER(LAYER_NUMBER)
    ) controller (
        .x_data_i(data_i),
        .x_valid_i(valid_i),
        .x_ready_o(ready_o),

        .h_data_i(h_data_lo),
        .h_valid_i(h_valid_lo),
        .h_ready_o(h_ready_lo),

        .data_o(lstm_data_mem_lo),
        .valid_o(lstm_valid_lo),
        .yumi_i(mac_ready_lo[0]), // note: this should work, since all MACs are identical, but it isn't ideal

        .clk_i,
        .rstb_i
    );

    // H queue to capture previous output
    hidden_state_queue #(
        .LENGTH(OUTPUT_LENGTH),
        .N_X(N_X)
    ) h_queue (
        .data_i(data_o),
        .valid_i(output_handshake),
        .ready_o(queue_ready_lo),

        .data_o(h_data_lo),
        .valid_o(h_valid_lo),
        .yumi_i(h_ready_lo),

        .clk_i,
        .rstb_i
    );

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin

            // MAC array communicating with controller
            cordic_mac_array #(
                .WIDTH(N_X),
                .FRACTIONAL_BITS(R_X),
                .N_INPUTS(INPUT_LENGTH+OUTPUT_LENGTH+1),
                .ARRAY_LENGTH(OUTPUT_LENGTH)
            ) mac_array (
                .data_i({lstm_data_lo, lstm_mem_lo[i]}),
                .valid_i(lstm_valid_lo),
                .ready_o(mac_ready_lo[i]),

                .data_o(mac_data_lo[i]),
                .valid_o(mac_valid_lo[i]),
                .yumi_i(piso_ready_lo[i]),

                .clk_i,
                .rstb_i
            );
        

            // PISO layers connecting with MAC
            piso #(
                .LAYER_HEIGHT(OUTPUT_LENGTH),
                .WORD_SIZE(N_X)
            ) piso_to_afb_layer (
                .clk_i,
                .reset_i(~rstb_i),

                .ready_o(piso_ready_lo[i]),
                .valid_i(mac_valid_lo[i]),
                .data_i(mac_data_lo[i]),

                .valid_o(piso_valid_lo[i]),
                .yumi_i(relu_ready_lo),
                .data_o(piso_data_lo[i])
            );
        end
    endgenerate

    // AFB block connecting to output
    lstm_relu_ideal #(
        .N(N_X)
    ) afb (
        .data_i(piso_data_lo),
        .valid_i(piso_valid_lo[0]),
        .ready_o(relu_ready_lo),

        .data_o,
        .valid_o(relu_valid_lo),
        .yumi_i(output_handshake),

        .clk_i,
        .rstb_i
    );

endmodule