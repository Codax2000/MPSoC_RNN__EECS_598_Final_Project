/**
Alex Knowlton
10/29/24

Ideal MAC array. Delays one cycle between each handshake to test robustness
of interfaces in other layer components, but computes sum of products. Data
input must be formatted as a packed array as follows:
{[N_X-1:0][[ARRAY_LENGTH-1:0][N_W-1:0]]}
 | X in   | packed weight array, N_W bits each |
*/

module mac_array #(
    parameter N_X=16,
    parameter N_W=16,
    parameter R_X=8,
    parameter R_W=8,
    parameter ARRAY_LENGTH=16,
    parameter N_SUMS=17
) (
    input logic valid_i,
    output logic ready_o,
    input logic [(N_X+ARRAY_LENGTH*N_W)-1:0] data_i,

    output logic [ARRAY_LENGTH-1:0][N_X-1:0] data_o,
    input logic yumi_i,
    output logic valid_o,

    input logic clk_i,
    input logic rstb_i
);

    logic signed [N_X-1:0] x_li;
    logic [ARRAY_LENGTH-1:0][N_W-1:0] mem_li;

    assign x_li = data_i[(N_X+ARRAY_LENGTH*N_W)-1:(N_X+ARRAY_LENGTH*N_W)-1-N_X];
    assign mem_li = data_i[(N_X+ARRAY_LENGTH*N_W)-1-N_X-1:0];

    logic [$clog2(N_SUMS)-1:0] count_n, count_r;
    enum logic {eADD, eVALID} ps_e, ns_e;

    assign ready_o = (ps_e == eADD) || (yumi_i);
    assign valid_o =  ps_e == eVALID;

    logic handshake_out, handshake_in;
    assign handshake_out = valid_o && yumi_i;
    assign handshake_in = valid_i && ready_o;

    always_comb begin
        case (ps_e)
            eADD: begin
                count_n = handshake_in ? count_r + 1 : count_r;
                ns_e = handshake_in && (count_r == (N_SUMS - 1)) ? eVALID : eADD;
            end
            eVALID: begin
                count_n = ~handshake_out ? count_r : 
                        handshake_in ? 1 : 0;
                ns_e = ~handshake_out ? eVALID :
                        handshake_in && (count_r == (N_SUMS - 1)) ? eVALID : eADD; 
            end
        endcase
    end
    
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            count_r <= '0;
            ps_e <= eADD;
        end else begin
            count_r <= count_n;
            ps_e <= ns_e;
        end
    end

    genvar i;
    generate
        for (i = 0; i < ARRAY_LENGTH; i = i + 1) begin
            ideal_mac # (
                .N_X(N_X),
                .N_W(N_W),
                .R_W(R_W),
                .R_X(R_X),
                .N_SUMS(N_SUMS)
            ) mac (
                .x_i(x_li),
                .w_i(mem_li[i]),
                .add_i(handshake_in),
                .clear_i(handshake_out),
                .clk_i,
                .rstb_i,
                .sum_o(data_o[i])
            );
        end
    endgenerate

endmodule