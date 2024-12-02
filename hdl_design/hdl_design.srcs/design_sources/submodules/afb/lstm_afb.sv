module lstm_afb #(
    parameter N=16,
    parameter R=12,
    parameter N_INPUTS=30
) (
    input logic [3:0][N-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    // IO signals of all handshake blocks
    logic i_sigmoid_valid_lo, i_sigmoid_ready_lo;
    logic signed [N-1:0] i_sigmoid_data_lo;

    logic u_tanh_valid_lo, u_tanh_ready_lo;
    logic signed [N-1:0] u_tanh_data_lo;

    logic f_sigmoid_valid_lo, f_sigmoid_ready_lo;
    logic signed [N-1:0] f_sigmoid_data_lo;

    logic o_sigmoid_valid_lo, o_sigmoid_ready_lo;
    logic signed [N-1:0] o_sigmoid_data_lo;

    logic mult1_valid_lo, mult1_ready_lo;
    logic signed [N-1:0] mult1_data_lo;

    logic c_adder_valid_lo, c_adder_ready_lo;
    logic signed [N-1:0] c_adder_data_lo;

    logic mult2_valid_lo, mult2_ready_lo;
    logic signed [N-1:0] mult2_data_lo;

    logic mult3_ready_lo;

    logic out_tanh_valid_lo, out_tanh_ready_lo;
    logic signed [N-1:0] out_tanh_data_lo;

    logic c_queue_valid_lo, c_queue_ready_lo;
    logic signed [N-1:0] c_queue_data_lo;

    // output signals and concatenated controls
    logic [5:0] valid_li;
    assign ready_o = i_sigmoid_ready_lo && u_tanh_ready_lo && f_sigmoid_ready_lo && o_sigmoid_ready_lo;
    assign valid_li[0] = ready_o && valid_i;
    assign valid_li[1] = mult1_ready_lo && i_sigmoid_valid_lo && u_tanh_valid_lo;
    assign valid_li[2] = mult2_ready_lo && f_sigmoid_valid_lo && c_queue_valid_lo;
    assign valid_li[3] = c_adder_ready_lo && mult1_valid_lo && mult2_valid_lo;
    assign valid_li[4] = c_queue_ready_lo && out_tanh_ready_lo && c_adder_valid_lo;
    assign valid_li[5] = mult3_ready_lo && o_sigmoid_valid_lo && out_tanh_valid_lo;

    afb #(
        .N(N),
        .R(R),
        .IS_TANH(1'b0)
    ) i_sigmoid (
        .data_i(data_i[0]),
        .ready_o(i_sigmoid_ready_lo),
        .valid_i(valid_li[0]),

        .data_o(i_sigmoid_data_lo),
        .valid_o(i_sigmoid_valid_lo),
        .yumi_i(valid_li[1]),

        .clk_i,
        .rstb_i
    );

    afb #(
        .N(N),
        .R(R),
        .IS_TANH(1'b1)
    ) u_tanh (
        .data_i(data_i[1]),
        .ready_o(u_tanh_ready_lo),
        .valid_i(valid_li[0]),

        .data_o(u_tanh_data_lo),
        .valid_o(u_tanh_valid_lo),
        .yumi_i(valid_li[1]),

        .clk_i,
        .rstb_i
    );

    afb #(
        .N(N),
        .R(R),
        .IS_TANH(1'b0)
    ) f_sigmoid (
        .data_i(data_i[2]),
        .ready_o(f_sigmoid_ready_lo),
        .valid_i(valid_li[0]),

        .data_o(f_sigmoid_data_lo),
        .valid_o(f_sigmoid_valid_lo),
        .yumi_i(valid_li[2]),

        .clk_i,
        .rstb_i
    );

    afb #(
        .N(N),
        .R(R),
        .IS_TANH(1'b0)
    ) o_sigmoid (
        .data_i(data_i[3]),
        .ready_o(o_sigmoid_ready_lo),
        .valid_i(valid_li[0]),

        .data_o(o_sigmoid_data_lo),
        .valid_o(o_sigmoid_valid_lo),
        .yumi_i(valid_li[5]),

        .clk_i,
        .rstb_i
    );

    cordic_mac_array #(
        .WIDTH(N),
        .FRACTIONAL_BITS(R),
        .N_INPUTS(1),
        .ARRAY_LENGTH(1),
        .INPUT_RESET_COUNT(0)
    ) mult1 (
        .clk_i,
        .rstb_i,
        
        .data_i({i_sigmoid_data_lo, u_tanh_data_lo}),
        .valid_i(valid_li[1]),
        .ready_o(mult1_ready_lo),

        .data_o(mult1_data_lo),
        .valid_o(mult1_valid_lo),
        .yumi_i(valid_li[3])
    );

    cordic_mac_array #(
        .WIDTH(N),
        .FRACTIONAL_BITS(R),
        .N_INPUTS(1),
        .ARRAY_LENGTH(1),
        .INPUT_RESET_COUNT(0)
    ) mult2 (
        .clk_i,
        .rstb_i,

        .data_i({c_queue_data_lo, f_sigmoid_data_lo}),
        .ready_o(mult2_ready_lo),
        .valid_i(valid_li[2]),

        .data_o(mult2_data_lo),
        .valid_o(mult2_valid_lo),
        .yumi_i(valid_li[3])
    );

    handshake_adder #(
        .N(N)
    ) c_adder (
        .clk_i,
        .rstb_i,

        .data_i({mult1_data_lo, mult2_data_lo}),
        .ready_o(c_adder_ready_lo),
        .valid_i(valid_li[3]),

        .data_o(c_adder_data_lo),
        .valid_o(c_adder_valid_lo),
        .yumi_i(valid_li[4])
    );
    
    c_queue #(
        .N(N),
        .LENGTH(N_INPUTS)
    ) c_feedback_queue (
        .clk_i,
        .rstb_i,

        .data_i(c_adder_data_lo),
        .ready_o(c_queue_ready_lo),
        .valid_i(valid_li[4]),

        .data_o(c_queue_data_lo),
        .valid_o(c_queue_valid_lo),
        .yumi_i(valid_li[2])
    );

    afb #(
        .N(N),
        .R(R),
        .IS_TANH(1'b1)
    ) out_tanh (
        .clk_i,
        .rstb_i,

        .data_i(c_adder_data_lo),
        .ready_o(out_tanh_ready_lo),
        .valid_i(valid_li[4]),

        .data_o(out_tanh_data_lo),
        .valid_o(out_tanh_valid_lo),
        .yumi_i(valid_li[5])
    );

    cordic_mac_array #(
        .WIDTH(N),
        .FRACTIONAL_BITS(R),
        .N_INPUTS(1),
        .ARRAY_LENGTH(1),
        .INPUT_RESET_COUNT(0)
    ) mult3 (
        .clk_i,
        .rstb_i,

        .data_i({out_tanh_data_lo, o_sigmoid_data_lo}),
        .ready_o(mult3_ready_lo),
        .valid_i(valid_li[5]),

        .data_o,
        .valid_o,
        .yumi_i
    );

endmodule