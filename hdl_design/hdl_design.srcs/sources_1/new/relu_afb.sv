module relu_afb #(
    parameter N = 16
) (
    input logic signed [N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,
    
    output logic signed [N-1:0] data_o,
    input logic yumi_i,
    output logic valid_o,
    
    input logic clk_i,
    input logic rstb_i
);
    enum logic {eFULL, eEMPTY} ps_e, ns_e;
    assign valid_o = ps_e == eFULL;
    assign ready_o = (ps_e == eEMPTY) || yumi_i;
    always_comb begin
        case(ps_e)
            eFULL: ns_e = yumi_i && ~valid_i ? eEMPTY : eFULL;
            eEMPTY: ns_e = valid_i ? eFULL : eEMPTY;
        endcase
    end
    
    // next data logic
    logic signed [N-1:0] data_o_n, data_o_r;
    assign data_o_n = (ready_o && valid_i) ? data_i : data_o_r;
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            data_o_r <= {N{1'b0}};
            ps_e <= eEMPTY;
        end else begin
            data_o_r <= data_o_n;
            ps_e <= ns_e;
        end
    end
    
    // ReLU function on output register, should help timing
    assign data_o = data_o_r[N-1] ? {N{1'b0}} : data_o_r;

endmodule