module piso #(
    parameter L = 10,
    parameter N = 16
) (
    input logic [L-1:0][N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,
    
    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,
    
    input logic clk_i,
    input logic rstb_i
);

    logic [L-1:0][N-1:0] data_captured;
    enum logic {eREADY, eSHIFTING} ps_e, ns_e;
    
    // count number of handshakes in
    assign valid_o = ps_e == eSHIFTING;
    logic [$clog2(L)-1:0] count_r, count_n;
    assign count_n = (valid_o && yumi_i) && (count_r == L - 1) ? 0 :
                     (valid_o && yumi_i) ? count_r + 1 : count_r;
    assign ready_o = (ps_e == eREADY) || ((valid_o && yumi_i) && (count_r == L - 1));
    always_comb begin
        case(ps_e)
            eREADY: ns_e = (ready_o && valid_i) ? eSHIFTING : eREADY;
            eSHIFTING: ns_e = ((valid_o && yumi_i) && (count_r == L - 1)) && ~(valid_i) ? eREADY : eSHIFTING;
        endcase
    end
    
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            ps_e <= eREADY;
            count_r <= '0;
        end else begin
            ps_e <= ns_e;
            count_r <= count_n;
        end
    end

endmodule