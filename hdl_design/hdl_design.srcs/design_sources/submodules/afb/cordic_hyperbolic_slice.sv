module cordic_hyperbolic_slice
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 8
)(
    input clk,
    input reset,
    input logic signed [WIDTH-1:0] x_in, 
    input logic signed [WIDTH-1:0] y_in, 
    input logic signed [WIDTH-1:0] z_in, 
    input logic signed [18:0] i,
    input expand,
    output logic signed [WIDTH-1:0] x_stage_out,
    output logic signed [WIDTH-1:0] y_stage_out, 
    output logic signed [WIDTH-1:0] z_stage_out
);


    logic signed [WIDTH-1:0] x_temp;
    logic signed [WIDTH-1:0] y_temp;
    logic signed [WIDTH-1:0] z_temp;

    logic signed [WIDTH-1:0] lut [0:16];
    logic signed [WIDTH-1:0] lut_expand[0:2];

    initial begin
        lut_expand[1] = 16'b0000000101011010; //arctanh(1-2^-1-2)
        lut_expand[0] = 16'b0000000011111001;
    end

    initial begin
        lut[0] = 16'b0000000000000000;
        lut[1] = 16'b0000000010001100; // arctanh(2^-1)
        lut[2] = 16'b0000000001000001;
        lut[3] = 16'b0000000000100000;
        lut[4] = 16'b0000000000010000;
        lut[5] = 16'b0000000000010000;
        lut[6] = 16'b0000000000001000;
        lut[7] = 16'b0000000000000100;
        lut[8] = 16'b0000000000000010;
        lut[9] = 16'b0000000000000001;
        lut[10] = 16'b0000000000000000;
        lut[11] = 16'b0000000000000000;
        lut[12] = 16'b0000000000000000;
        lut[13] = 16'b0000000000000000;
        lut[14] = 16'b0000000000000000;
        lut[15] = 16'b0000000000000000;
        lut[16] = 16'b0000000000000000;
    end


    
    always_comb begin
        if (expand) begin
            if (z_in < 0) begin
                x_temp = x_in - (y_in - (y_in >>> (i + 2))); 
                y_temp = y_in - (x_in - (x_in >>> (i + 2)));
                z_temp = z_in + lut_expand[i]; 

            end else begin    
                x_temp = x_in + (y_in - (y_in >>> (i + 2))); 
                y_temp = y_in + (x_in - (x_in >>> (i + 2)));
                z_temp = z_in - lut_expand[i];
            end
        end
        else begin
            if (z_in < 0) begin
                x_temp = x_in - (y_in >>> i);
                y_temp = y_in - (x_in >>> i);
                z_temp = z_in + lut[i];
            end else begin
                x_temp = x_in + (y_in >>> i);
                y_temp = y_in + (x_in >>> i);
                z_temp = z_in - lut[i];
            end
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
