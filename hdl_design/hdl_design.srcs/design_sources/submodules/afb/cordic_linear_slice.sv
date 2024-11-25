module cordic_linear_slice
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 8
)(
    input clk,
    input reset, 
    input logic signed [WIDTH-1:0]x_in, 
    input logic signed [WIDTH-1:0]y_in, 
    input logic signed [WIDTH-1:0]z_in, 
    input logic signed [18:0] i,
    output logic signed [WIDTH-1:0]x_stage_out,
    output logic signed [WIDTH-1:0]y_stage_out, 
    output logic signed [WIDTH-1:0]z_stage_out
);


    logic signed [WIDTH-1:0] x_temp;
    logic signed [WIDTH-1:0] y_temp;
    logic signed [WIDTH-1:0] z_temp;


    always_comb begin 
        if (y_in < 0) begin
            x_temp = x_in;
            y_temp = y_in + (x_in >>> i);
            z_temp = z_in - (1 <<<FRACTIONAL_BITS) >>> i;
        end else begin
            x_temp = x_in;
            y_temp = y_in - (x_in >>> i);
            z_temp = z_in + (1 <<<FRACTIONAL_BITS) >>> i;
        end
    end

    always_ff @ (posedge clk) 
    begin
        if (reset) begin
            x_stage_out <= 18'd0;
            y_stage_out <= 18'd0;
            z_stage_out <= 18'd0;
        end
        else begin
            x_stage_out <= x_temp;
            y_stage_out <= y_temp;
            z_stage_out <= z_temp;
        end
    end

endmodule
