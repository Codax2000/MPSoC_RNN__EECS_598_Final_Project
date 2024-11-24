/**
Alex Knowlton
11/23/24

Module for toplevel LSTM network. Contains all 5 layers from LSTM paper. 

Accepts standard handshakes
*/

module geo_net #(
    parameter N=16,
    parameter R=8
) (
    input logic signed [N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic signed [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i
);

    // first fully-connected layer
    logic signed [N-1:0]    data_lo1, data_lo2, data_lo3, data_lo4;
    logic                   valid_lo1, valid_lo2, valid_lo3, valid_lo4;
    logic                   ready_lo2, ready_lo3, ready_lo4, ready_lo5;

    fc_layer #(
        .R_X(8),
        .R_W(8),
        .LAYER_NUMBER(1),
        .INPUT_LENGTH(90),
        .OUTPUT_LENGTH(60)
    ) layer_1 (
        .data_i,
        .ready_o,
        .valid_i,

        .clk_i,
        .rstb_i,

        .data_o(data_lo1),
        .valid_o(valid_lo1),
        .yumi_i(ready_lo2)
    );

    fc_layer #(
        .R_X(8),
        .R_W(8),
        .LAYER_NUMBER(2),
        .INPUT_LENGTH(60),
        .OUTPUT_LENGTH(30)
    ) layer_2 (
        .data_i(data_lo1),
        .ready_o(ready_lo2),
        .valid_i(valid_lo1),

        .clk_i,
        .rstb_i,

        .data_o(data_lo2),
        .valid_o(valid_lo2),
        .yumi_i(ready_lo3)
    );

    lstm_layer #(
        .R_X(8),
        .R_W(8),
        .LAYER_NUMBER(5), // this is for memory file indexing, LSTM takes 5-8
        .INPUT_LENGTH(30),
        .OUTPUT_LENGTH(40)
    ) layer_3 (
        .data_i(data_lo2),
        .ready_o(ready_lo3),
        .valid_i(valid_lo2),

        .clk_i,
        .rstb_i,

        .data_o(data_lo3),
        .valid_o(valid_lo3),
        .yumi_i(ready_lo4)        
    );

    fc_layer #(
        .R_X(8),
        .R_W(8),
        .LAYER_NUMBER(3),
        .INPUT_LENGTH(40),
        .OUTPUT_LENGTH(20)
    ) layer_4 (
        .data_i(data_lo3),
        .ready_o(ready_lo4),
        .valid_i(valid_lo3),

        .clk_i,
        .rstb_i,

        .data_o(data_lo4),
        .valid_o(valid_lo4),
        .yumi_i(ready_lo5)
    );

    fc_layer #(
        .R_X(8),
        .R_W(8),
        .LAYER_NUMBER(4),
        .INPUT_LENGTH(20),
        .OUTPUT_LENGTH(1)
    ) layer_5 (
        .data_i(data_lo4),
        .ready_o(ready_lo5),
        .valid_i(valid_lo4),

        .clk_i,
        .rstb_i,

        .data_o,
        .valid_o,
        .yumi_i
    );

endmodule