module toplevel #(
    parameter N=16
) (
    input signed [N-1:0] data_i,
    input valid_i,
    output reg ready_o,

    output reg signed [N-1:0] data_o,
    output reg valid_o,
    input yumi_i,

    input clk_i,
    input rstb_i
);
    wire [N-1:0] lstm_data_lo;
    wire lstm_valid_lo;
    wire lstm_yumi_i;

    wire fc1_ready_lo;
    wire [N-1:0]fc1_data_lo;
    wire fc1_valid_lo;

    wire tanh1_ready_lo;
    wire [N-1:0]tanh1_data_lo;
    wire tanh1_valid_lo;

    wire [N-1:0]fc2_data_lo;
    wire fc2_ready_lo;
    wire fc2_valid_lo;

    wire tanh2_ready_lo;
    wire [N-1:0]tanh2_data_lo;
    wire tanh2_valid_lo;


    lstm_layer toplevel_net (
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
        .LAYER_NUMBER=2
        .INPUT_LENGTH=40
        .OUTPUT_LENGTH=20
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
        .LAYER_NUMBER=3
        .INPUT_LENGTH=20
        .OUTPUT_LENGTH=1
    )fc2(
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
        .valid_i(tanh2_valid_lo),
        
        .data_o(data_o),
        .valid_o(valid_o),
        .yumi_i(yumi_i),
        
        .clk_i(clk_i),
        .rstb_i(rstb_i)
    );

    

endmodule