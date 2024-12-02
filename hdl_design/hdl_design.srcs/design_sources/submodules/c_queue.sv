module c_queue #(
    parameter N=16,
    parameter LENGTH=30
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

    enum logic {eFULL, eREADY} ps_e, ns_e;
    logic [LENGTH-1:0][N-1:0] data_r, data_n;
    logic handshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;
    assign valid_o = ps_e == eFULL;
    assign ready_o = ps_e == eREADY || yumi_i;
    assign data_n = handshake_in ? {data_i, data_r[LENGTH-1:1]} : data_r;
    assign data_o = data_r[0];

    always_comb begin
        case (ps_e)
            eFULL: ns_e = yumi_i && (!valid_i) ? eREADY : eFULL;
            eREADY: ns_e = valid_i ? eFULL : eREADY;
        endcase
    end

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            ps_e <= eFULL;
            data_r <= '0;
        end else begin
            ps_e <= ns_e;
            data_r <= data_n;
        end
    end

endmodule