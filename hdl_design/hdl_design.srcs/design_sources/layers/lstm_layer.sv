/**
Alex Knowlton
11/2/2024

LSTM layer. Has standard handshakes at input and output.

parameters:
    N_X - number of bits in X word
    N_W - number of bits in W word
    R_X - number of fractional bits in X
    R_W - number of fractional bits in W
    INPUT_LENGTH - length of input vector X
    OUTPUT_LENGTH - length of output vector Y
    LAYER_NUMBER - index of the layer in the network, used for memory files
*/

module lstm_layer #(
    parameter N_X=16,
    parameter N_W=8,
    parameter R_X=8,
    parameter R_W=8,
    parameter INPUT_LENGTH=16,
    parameter OUTPUT_LENGTH=8,
    parameter LAYER_NUMBER=5
) (
    input logic [N_X-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [N_X-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

// controller to feed data from input to MAC and select betwen X and H

// H queue to capture previous output

// MAC array communicating with controller

// PISO layers connecting with MAC

// AFB block connecting to output

endmodule