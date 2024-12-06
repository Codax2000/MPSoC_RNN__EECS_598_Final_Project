/**
Alex Knowlton and Akash Shetty
12/4/24

Module with an LSTM layer followed by 2 fully connected layers for test
prediction comparison with the reference model.
*/

module pytorch_toplevel #(
    parameter N=16
) (
    input logic signed [N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic signed [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);
    logic signed [N-1:0] lstm_data_lo;
    logic lstm_valid_lo;
    logic lstm_yumi_i;

    logic fc1_ready_lo;
    logic signed [N-1:0] fc1_data_lo;
    logic fc1_valid_lo;

    logic tanh1_ready_lo;
    logic signed [N-1:0] tanh1_data_lo;
    logic tanh1_valid_lo;

    logic signed [N-1:0]fc2_data_lo;
    logic fc2_ready_lo;
    logic fc2_valid_lo;

    logic tanh2_ready_lo;
    logic signed [N-1:0]tanh2_data_lo;
    logic tanh2_valid_lo;

    lstm_layer #(
        .N_X(16),
        .N_W(16),
        .R_X(12),
        .R_W(12),
        .INPUT_LENGTH(30),
        .OUTPUT_LENGTH(40),
        .LAYER_NUMBER(4)
    ) toplevel_net (
        .data_i(data_i),
        .ready_o(ready_o),
        .valid_i(valid_i),
        
        .data_o(lstm_data_lo),
        .valid_o(lstm_valid_lo),
        .yumi_i(fc1_ready_lo),
        
        .clk_i(clk_i),
        .rstb_i(rstb_i)
    );


    fc_layer #(
        .LAYER_NUMBER(2),
        .INPUT_LENGTH(40),
        .OUTPUT_LENGTH(20)
    )fc1(
        .clk_i(clk_i),
        .rstb_i(rstb_i),

        .data_i(lstm_data_lo),
        .valid_i(lstm_valid_lo),
        .ready_o(fc1_ready_lo),

        .data_o(fc1_data_lo),
        .valid_o(fc1_valid_lo),
        .yumi_i(tanh1_ready_lo)
    );
    

    afb tanh1(
        .data_i(fc1_data_lo),
        .ready_o(tanh1_ready_lo),
        .valid_i(fc1_valid_lo),
        
        .data_o(tanh1_data_lo),
        .valid_o(tanh1_valid_lo),
        .yumi_i(fc2_ready_lo),
        
        .clk_i(clk_i),
        .rstb_i(rstb_i)

    );

    fc_layer #(
        .LAYER_NUMBER(3),
        .INPUT_LENGTH(20),
        .OUTPUT_LENGTH(1)
    ) fc2 (
        .clk_i(clk_i),
        .rstb_i(rstb_i),

        .data_i(tanh1_data_lo),
        .valid_i(tanh1_valid_lo),
        .ready_o(fc2_ready_lo),

        .data_o(fc2_data_lo),
        .valid_o(fc2_valid_lo),
        .yumi_i(tanh2_data_lo)
    );

    afb tanh2(
        .data_i(fc2_data_lo),
        .ready_o(tanh2_data_lo),
        .valid_i(fc2_valid_lo),
        
        .data_o(data_o),
        .valid_o(valid_o),
        .yumi_i(yumi_i),
        
        .clk_i(clk_i),
        .rstb_i(rstb_i)
    );

   
endmodule