/**
Alex Knowlton
11/12/24

array of cordic MAC to replace DSP slices, uses standard handshakes
*/

module cordic_mac_array
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 12,
    parameter N_INPUTS = 6,
    parameter ARRAY_LENGTH = 1
)
(
    input logic clk_i,
    input logic rstb_i,
    input logic [(1+ARRAY_LENGTH)-1:0][WIDTH-1:0] data_i,
    input logic valid_i,
    input logic yumi_i,
    output logic [ARRAY_LENGTH-1:0][WIDTH-1:0] data_o,
    output logic valid_o,
    output logic ready_o
);

    logic [WIDTH-1:0] z_input;
    logic [ARRAY_LENGTH-1:0][WIDTH-1:0] x_input;

    assign z_input = data_i[ARRAY_LENGTH];
    assign x_input = data_i[ARRAY_LENGTH-1:0];

    logic [$clog2(N_INPUTS)-1:0] input_counter_n, input_counter_r;
    logic [$clog2(FRACTIONAL_BITS)-1:0] iterate_counter_n, iterate_counter_r;

    enum logic [2:0] {eITERATE, eSAMPLE, eDONE} ps_e, ns_e;
    logic iterate, clear;

    assign valid_o = ps_e == eDONE;
    assign ready_o = (ps_e == eSAMPLE) || (valid_o && yumi_i); 
    assign iterate = ps_e == eITERATE;
    assign clear = valid_o && yumi_i;

    genvar i;
    generate
        for (i = 0; i < ARRAY_LENGTH; i = i + 1) begin
            cordic_mac_slice mac_slice (
                .clk_i,
                .rstb_i,
                .iterate,
                .clear,
                .index(iterate_counter_r),
                .x_i(x_input[i]),
                .z_i(z_input),
                .y_o(data_o[i])
            );
        end
    endgenerate

    always_comb begin
        case (ps_e)
            eSAMPLE: begin
                ns_e = valid_i ? eITERATE : eSAMPLE;
                input_counter_n = valid_i ? input_counter_r + 1 : input_counter_r;
                iterate_counter_n = '0;
            end
            eITERATE: begin
                ns_e = (iterate_counter_r != (FRACTIONAL_BITS - 1)) ? eITERATE : 
                        (input_counter_r == (N_INPUTS - 1)) ? eDONE : eSAMPLE;
                input_counter_n = input_counter_r;
                iterate_counter_n = iterate_counter_n + 1;
            end
            eDONE: begin
                ns_e = ~yumi_i ? eDONE : valid_i ? eITERATE : eSAMPLE;
                input_counter_n = '0;
                iterate_counter_n = '0;
            end
            default: begin
                ns_e = valid_i ? eITERATE : eSAMPLE;
                input_counter_n = valid_i ? input_counter_r + 1 : input_counter_r;
                iterate_counter_n = '0;
            end
        endcase
    end

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            ps_e <= eSAMPLE;
            iterate_counter_r = '0;
            input_counter_r = '0;
        end else begin
            ps_e <= ns_e;
            iterate_counter_r <= iterate_counter_n;
            input_counter_r <= input_counter_n;
        end
    end
endmodule
