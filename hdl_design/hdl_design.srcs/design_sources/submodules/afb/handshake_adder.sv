module handshake_adder # (
    parameter N=16
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

    logic signed [N-1:0] a, b, sum, data_o_n;
    assign a = data_i[0];
    assign b = data_i[1];
    assign sum = a + b;

    enum logic {eREADY, eFULL} ps_e, ns_e;
    logic handshake_in, handshake_out;
    assign data_o_n = handshake_in ? sum : data_o;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;

    always_comb begin
        case (ps_e)
            eREADY: ns_e = handshake_in ? eFULL : eREADY;
            eFULL: ns_e = handshake_out && !handshake_in ? eREADY : eFULL;
        endcase
    end

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            ps_e <= eREADY;
            data_o <= '0;
        end else begin
            ps_e <= ns_e;
            data_o <= data_o_n;
        end
    end

endmodule