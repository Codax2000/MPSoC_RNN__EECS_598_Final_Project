module afb_hyperbolic_handshake #(
    parameter N=16,
    parameter R=8
) (
    input logic [N-1:0] data_i, // theta
    input logic valid_i,
    output logic ready_o,

    output logic [1:0][N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i
);


endmodule