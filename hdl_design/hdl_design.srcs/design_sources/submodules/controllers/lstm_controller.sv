/**
Alex Knowlton
11/2/2024

Controller for the LSTM layer. Works much like the controller for the fully-
connected layer, but has 2 ready/valid input handshakes - one for the
hidden state and one for the input X vector.

parameters:
    N_X - number of bits in X word
    N_W - number of bits in W word
    R_X - number of fractional bits in X
    R_W - number of fractional bits in W
    INPUT_LENGTH - length of input vector X
    OUTPUT_LENGTH - length of output vector Y
    LAYER_NUMBER - index of the layer in the network, used for memory files
*/

module lstm_controller #(
    parameter N_X=16,
    parameter N_W=8,
    parameter R_X=8,
    parameter R_W=8,
    parameter INPUT_LENGTH=4,
    parameter OUTPUT_LENGTH=3,
    parameter LAYER_NUMBER=6
) (
    input logic [N_X-1:0] x_data_i,
    input logic x_valid_i,
    output logic x_ready_o,

    input logic [N_X-1:0] h_data_i,
    input logic h_valid_i,
    output logic h_ready_o,

    output logic [N_X-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    localparam logic [N_BITS_DATA-1:0] ONE = (1 << (R_BITS_DATA));

    // handshake signals for convenience
    logic [N_X-1:0] selected_data_input;
    logic ready, valid;
    logic handshake_in, handshake_out;
    logic counting_x = addr_n < N_INPUTS;
    assign x_ready_o = ready && counting_x;
    assign h_ready_o = ready && !counting_x;
    assign valid = counting_x ? x_valid_i : h_valid_i;
    assign handshake_in = ready && valid;
    assign handshake_out = valid_o && yumi_i;
    assign selected_data_input = counting_x ? x_data_i : h_data_i;

    // signals used to pass data around, including memory
    logic [$clog2(N_INPUTS+N_OUTPUTS+1)-1:0] addr_r, addr_n;
    logic [3:0][N_OUTPUTS-1:0][N_BITS_MEM-1:0] mem_data_lo;
    logic [N_BITS_DATA-1:0] data_i_r, data_i_n;

    // state logic
    enum logic [1:0] {eREADY, eFULL, eBIAS} ps_e, ns_e;

    // assign outputs and registers
    assign valid_o = (ps_e == eBIAS) || (ps_e == eFULL);
    assign data_o = ps_e == eBIAS ? {ONE, mem_data_lo} : {data_i_r, mem_data_lo};
    assign data_i_n = handshake_in ? selected_data_input : data_i_r;

    // state logic
    always_comb begin
        case (ps_e)
            eREADY: begin
                ready = 1'b1;
                ns_e = handshake_in ? eFULL : eREADY;
                addr_n = addr_r;
            end
            eFULL: begin
                ready = handshake_out && (addr_r != N_INPUTS - 1);
                ns_e = (~handshake_out) ? eFULL :
                       (addr_r == N_INPUTS - 1) ? eBIAS : 
                       (handshake_in) ? eFULL: eREADY;
                addr_n = handshake_out ? addr_r + 2'b01 : addr_r; 
            end
            eBIAS: begin
                ready = handshake_out;
                addr_n = handshake_out ? 0 : addr_r;
                ns_e = (~handshake_out) ? eBIAS :
                       (handshake_in) ? eFULL : eREADY;
            end
            default: begin
                ready = 1'b1;
                ns_e = handshake_in ? eFULL : eREADY;
                addr_n = addr_r;
            end
        endcase
    end

    // sequential block
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            addr_r <= '0;
            data_i_r <= '0;
            ps_e <= eREADY;
        end else begin
            addr_r <= addr_n;
            data_i_r <= data_i_n;
            ps_e <= ns_e;
        end
    end

    // instantiate memories
    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin
            mem_array #(
                .N_BITS(N_BITS_MEM),
                .LAYER_NUMBER(LAYER_NUMBER + i),
                .ARRAY_LENGTH(N_OUTPUTS),
                .N_WEIGHTS(N_INPUTS+1)
            ) memories (
                .addr_i(addr_n),
                .clk_i,
                .data_o(mem_data_lo[i])
            );
        end
    endgenerate

endmodule