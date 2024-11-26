module cordic_linear
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 8,
    parameter NUM_ITERATIONS = 16
)(
    input clk,
    input reset, 
    input signed [WIDTH-1:0]x_in, 
    input signed [WIDTH-1:0]y_in, 
    input signed [WIDTH-1:0]z_in, 
    output logic signed [WIDTH-1:0]x_out,
    output logic signed [WIDTH-1:0]y_out, 
    output logic signed [WIDTH-1:0]z_out
);

 
    logic signed [WIDTH-1:0] x_stage [0:15];
    logic signed [WIDTH-1:0] y_stage [0:15];
    logic signed [WIDTH-1:0] z_stage [0:15];

    assign x_stage[0] = x_in;
    assign y_stage[0] = y_in;
    assign z_stage[0] = z_in; 

    
    genvar i;
    generate
        for (i = 0; i < 15; i = i + 1) begin
            cordic_linear_slice stage
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i]),
                .y_in(y_stage[i]),
                .z_in(z_stage[i]),
                .i(18'd0 + i), 
                .x_stage_out(x_stage[i+1]),
                .y_stage_out(y_stage[i+1]),
                .z_stage_out(z_stage[i+1])
            );
        end
    endgenerate

  
    assign x_out = x_stage[15];
    assign y_out = y_stage[15];
    assign z_out = z_stage[15];
    

endmodule