module cordic_hyperbolic#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 8
    parameter NUM_ITERATIONS = 16
)(
    input clk, 
    input reset, 
    input logic signed [WIDTH-1:0] x_in,
    input logic signed [WIDTH-1:0] y_in, 
    input logic signed [WIDTH-1:0] z_in, 

    output logic signed [WIDTH-1:0] x_out,
    output logic signed [WIDTH-1:0] y_out,
    output logic signed [WIDTH-1:0] z_out,
)

    
    logic signed [WIDTH-1:0] x_stage [0:17];
    logic signed [WIDTH-1:0] y_stage [0:17];
    logic signed [WIDTH-1:0] z_stage [0:17];

    assign x_stage[0] = x_in;
    assign y_stage[0] = y_in;
    assign z_stage[0] = z_in; 

    cordic_hyperbolic_slice expand1
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i]),
                .y_in(y_stage[i]),
                .z_in(z_stage[i]),
                .i(18'd0 + 1), 
                .expand(1),
                .x_stage_out(x_stage[i+1]),
                .y_stage_out(y_stage[i+1]),
                .z_stage_out(z_stage[i+1])
            );

    cordic_hyperbolic_slice expand2
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i]),
                .y_in(y_stage[i]),
                .z_in(z_stage[i]),
                .i(18'd0), 
                .expand(1),
                .x_stage_out(x_stage[i+1]),
                .y_stage_out(y_stage[i+1]),
                .z_stage_out(z_stage[i+1])
            );

    genvar i;
    generate
        for (i = 1; i < 17; i = i + 1) begin
            cordic_hyperbolic_slice stage
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i+1]),
                .y_in(y_stage[i+1]),
                .z_in(z_stage[i+1]),
                .i(18'd0 + i), 
                .expand(0)
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