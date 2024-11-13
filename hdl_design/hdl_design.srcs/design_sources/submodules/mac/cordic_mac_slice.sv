module cordic_mac_slice #(
    parameter N_X=16,
    parameter R_X=12
) (
    input logic signed [N_X-1:0] x_i,
    input logic signed [N_X-1:0] z_i,
    input logic [$clog2(R_X)-1:0] index,
    input logic clk_i,
    input logic rstb_i,
    input logic iterate,
    input logic clear,
    output logic signed [N_X-1:0] y_o
);

    logic signed [N_X-1:0] y_n, x_shift, x_shift_neg, x_shift_sel;
    logic dir;
    assign dir = index == 0 ? z_i < 0 : ~z_i[R_X - index];
    
    assign x_shift = x_i >>> (index + 1);
    assign x_shift_neg = ~x_shift + 1;
    assign x_shift_sel = dir ? x_shift_neg : x_shift;
    assign y_n = clear ? '0 : iterate ? y_o + x_shift_sel : y_o;

    always_ff @(posedge clk_i) begin
        if (~rstb_i)
            y_o <= '0;
        else
            y_o <= y_n;
    end

endmodule