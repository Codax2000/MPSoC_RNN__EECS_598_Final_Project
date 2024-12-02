module toplevel (
    input signed [N-1:0] data_i,
    input valid_i,
    output reg ready_o,

    output reg signed [N-1:0] data_o,
    output reg valid_o,
    input yumi_i,
    
    input clk_i,
    input rstb_i
);

    lstm_layer toplevel_net (
        .data_i(data_i),
        .valid_i(valid_i),
        .ready_o(ready_o),
        
        .data_o,
        .valid_o,
        .yumi_i,
        
        .clk_i,
        .rstb_i
    );

endmodule