/**
Alex Knowlton
11/2/2024

queue for hidden state variables of LSTM layer. captures data as it is
handshaked out to the next layer and handshakes it back to the start of the
LSTM network. Can only handshake in until full and handshake out until empty,
so not a normal queue.

parameters:
LENGTH: number of elements in the queue
N_X: number of bits per word
*/

module hidden_state_queue #(
    parameter LENGTH=16,
    parameter N_X=16
) (
    input logic [N_X-1:0] data_i,
    input valid_i,
    output ready_o,

    output logic [N_X-1:0] data_o,
    output valid_o,
    input yumi_i,

    input clk_i,
    input rstb_i
);

    localparam logic [N_X-1:0] ZERO = 0;

    logic [$clog2(LENGTH)-1:0] count_r, count_n;
    logic [LENGTH-1:0][N_X-1:0] shift_n, shift_r;
    enum logic {eFILLING, eDRAINING} ps_e, ns_e;
    logic handshake_in, handshake_out;

    assign handshake_in = ready_o && valid_i;
    assign handshake_out = valid_o && yumi_i;
    assign valid_o = ps_e == eDRAINING;
    assign ready_o = ps_e == eFILLING;
    assign data_o = shift_r[0];
    assign shift_n = handshake_in || handshake_out ? {data_i, shift_r[LENGTH-1:1]} : shift_r;

    always_comb begin
        case(ps_e)
            eDRAINING: begin
                count_n = handshake_out ? count_r - 1 : count_r;
                ns_e = handshake_out && (count_r == 1) ? eFILLING : eDRAINING;
            end
            eFILLING: begin
                count_n = handshake_in ? count_r + 1 : count_r;
                ns_e = handshake_in && (count_r == (LENGTH - 1)) ? eDRAINING : eFILLING;
            end
        endcase
    end

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            shift_r <= '0;
            ps_e <= eDRAINING; // this is so that the LSTM layer can run
            count_r <= LENGTH; // count down while draining, up while filling
        end else begin
            shift_r <= shift_n;
            ps_e <= ns_e;
            count_r <= count_n;
        end
    end

endmodule