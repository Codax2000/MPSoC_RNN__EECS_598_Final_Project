module afb_linear_handshake #(
    parameter N=16,
    parameter R=8,
    parameter logic IS_TANH=1
) (
    input logic [1:0][N-1:0] data_i, // theta
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i
);


endmodule