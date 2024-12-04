module toplevel #(
    parameter N=16
) (
    input signed [N-1:0] data_i,
    input valid_i,
    output wire ready_o,

    output wire signed [N-1:0] data_o,
    output wire valid_o,
    input yumi_i,

    input clk_i,
    input rstb_i
);

    // Internal signals
    wire signed [N-1:0] data_o_wire;
    wire valid_o_wire;

    // Assign internal signals to output ports
    assign data_o = data_o_wire;
    assign valid_o = valid_o_wire;
    
    lstm_layer toplevel_net (
        .data_i(data_i),
        .ready_o(ready_o),
        .valid_i(valid_i),
        
        .data_o(data_o_wire),
        .valid_o(valid_o_wire),
        .yumi_i(yumi_i),
        
        .clk_i(clk_i),
        .rstb_i(rstb_i)
    );

endmodule