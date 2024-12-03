module cordic_mac_slice #(
    parameter N_X=16,
    parameter R_X=12,
    parameter N_INPUTS=6
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

    localparam logic [$clog2(R_X)-1:0] R_local = R_X;
    logic [$clog2(R_X)-1:0] diff;
    logic signed [$clog2(N_INPUTS)+N_X+1:0] y_extended, y_n, x_shift_sel_ext;
    assign diff = R_local - index;

    logic signed [N_X-1:0] x_shift, x_shift_neg, x_shift_sel;
    logic dir;
    assign dir = index == 0 ? z_i[N_X-1] : ~z_i[diff];
    
    assign x_shift = x_i >>> (index + 1);
    assign x_shift_neg = ~x_shift + 1;
    assign x_shift_sel = dir ? x_shift_neg : x_shift;
    assign x_shift_sel_ext[N_X-1:0] = x_shift_sel;
    assign x_shift_sel_ext[$clog2(N_INPUTS)+N_X+1:N_X] = {{$clog2(N_INPUTS)+2}{x_shift_sel[N_X-1]}};
    assign y_n = clear ? '0 : iterate ? y_extended + x_shift_sel_ext : y_extended;

    always_ff @(posedge clk_i) begin
        if (~rstb_i)
            y_extended <= '0;
        else
            y_extended <= y_n;
    end

    // assign y_o
    localparam logic signed [N_X-1:0] MAX_VALUE = 16'h7FFF;
    localparam logic signed [N_X-1:0] MIN_VALUE = 16'h8000;
    assign y_o = y_extended > MAX_VALUE ? MAX_VALUE :
                 y_extended < MIN_VALUE ? MIN_VALUE : y_extended[N_X-1:0];

endmodule
