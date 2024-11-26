module cordic_hyperbolic#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 8,
    parameter NUM_ITERATIONS = 16
)(
    input clk, 
    input reset, 
    input logic signed [WIDTH-1:0] x_in,
    input logic signed [WIDTH-1:0] y_in, 
    input logic signed [WIDTH-1:0] z_in, 

    output logic signed [WIDTH-1:0] x_out,
    output logic signed [WIDTH-1:0] y_out,
    output logic signed [WIDTH-1:0] z_out
);

    
    logic signed [WIDTH-1:0] x_stage [0:17];
    logic signed [WIDTH-1:0] y_stage [0:17];
    logic signed [WIDTH-1:0] z_stage [0:17];

    assign x_stage[0] = x_in;
    assign y_stage[0] = y_in;
    assign z_stage[0] = z_in; 

    logic [18:0] i_values [0:NUM_ITERATIONS-1];

    initial begin
        i_values[0] = 1;
        i_values[1] = 2;
        i_values[2] = 3;
        i_values[3] = 4;
        i_values[4] = 4;
        i_values[5] = 5;
        i_values[6] = 6;
        i_values[7] = 7;
        i_values[8] = 8;
        i_values[9] = 9;
        i_values[10] = 10;
        i_values[11] = 11;
        i_values[12] = 12;
        i_values[13] = 13;
        i_values[14] = 13;
        i_values[15] = 14;


    end
    cordic_hyperbolic_slice expand1
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[0]),
                .y_in(y_stage[0]),
                .z_in(z_stage[0]),
                .i(18'd0 + 1), 
                .expand(1),
                .x_stage_out(x_stage[1]),
                .y_stage_out(y_stage[1]),
                .z_stage_out(z_stage[1])
            );

    cordic_hyperbolic_slice expand2
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[1]),
                .y_in(y_stage[1]),
                .z_in(z_stage[1]),
                .i(18'd0), 
                .expand(1),
                .x_stage_out(x_stage[2]),
                .y_stage_out(y_stage[2]),
                .z_stage_out(z_stage[2])
            );

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            cordic_hyperbolic_slice stage
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i+1]),
                .y_in(y_stage[i+1]),
                .z_in(z_stage[i+1]),
                .i(i_values[i]), 
                .expand(0),
                .x_stage_out(x_stage[i+2]),
                .y_stage_out(y_stage[i+2]),
                .z_stage_out(z_stage[i+2])
            );
        end
    endgenerate

  
    assign x_out = x_stage[17];
    assign y_out = y_stage[17];
    assign z_out = z_stage[17];


endmodule