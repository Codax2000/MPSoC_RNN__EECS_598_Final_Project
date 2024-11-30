module single_queue #(
    parameter N=16
) (
    input logic [N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    logic [N-1:0] data_o_n;
    logic handshake_in, handshake_out;

    enum logic {eFULL, eEMPTY} ps_e, ns_e;
    assign valid_o = ps_e == eFULL;
    assign ready_o = (ps_e == eEMPTY) || yumi_i;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;
    assign data_o_n = handshake_in ? data_i : data_o;

    always_comb begin
        case (ps_e)
            eFULL: ns_e = handshake_out && ~handshake_in ? eEMPTY : eFULL;
            eEMPTY: ns_e = handshake_in ? eFULL : eEMPTY;
        endcase
    end

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            data_o <= '0;
            ps_e <= eEMPTY;
        end else begin
            data_o <= data_o_n;
            ps_e <= ns_e;
        end
    end

endmodule