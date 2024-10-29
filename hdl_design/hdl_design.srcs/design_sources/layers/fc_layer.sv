

module fc_layer #(
    parameter L=10,
    parameter N=16
)(
    input logic clk_i,
    input logic rstb_i,
    
    input logic signed [N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,
    
    output logic [L-1:0][N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i
);


endmodule
