module lstm_afb #(
    parameter N=16,
    parameter R=12,
    parameter N_INPUTS=30
) (
    input logic [1:0][N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    afb #(
        // TODO: Fill in parameters
    ) i_sigmoid (
        // TODO: Fill IO
    );

    afb #(
        // TODO: Fill in parameters
    ) u_tanh (
        // TODO: Fill IO
    );

    afb #(
        // TODO: Fill in parameters
    ) f_sigmoid (
        // TODO: Fill IO
    );

    afb #(
        // TODO: Fill in parameters
    ) o_sigmoid (
        // TODO: Fill IO
    );

    cordic_mac_array #(
        // TODO: Fill in parameters
    ) mult1 (
        // TODO: Fill IO
    );

    cordic_mac_array #(
        // TODO: Fill in parameters
    ) mult2 (
        // TODO: Fill IO
    );

    handshake_adder #(
        // TODO: Fill in parameters
    ) c_adder (
        // TODO: Fill IO
    );
    
    hidden_state_queue #(
        // TODO: Fill in parameters
    ) c_queue (
        // TODO: Fill IO
    );

    afb #(
        // TODO: Fill in parameters
    ) out_tanh (
        // TODO: Fill IO
    );

    cordic_mac_array #(
        // TODO: Fill in parameters
    ) mult3 (
        // TODO: Fill IO
    );

endmodule