module toplevel #(
    parameter N=16
) (
    input signed [N-1:0] data_i,
    input valid_i,
    output reg ready_o,

    output reg signed [N-1:0] data_o,
    output reg valid_o,
    input yumi_i
);

    lstm_layer toplevel_net (.*);

endmodule