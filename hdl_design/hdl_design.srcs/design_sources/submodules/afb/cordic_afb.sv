module cordic_afb(
    input clk, 
    input reset, 
    input lut_hyperbolic,
    input tanh, 
    input signed [15:0] x_in,
    input signed [15:0] y_in,
    input signed [15:0] z_in,
    output logic signed [15:0] x_out
    output logic signed [15:0] y_out
    output logic signed [15:0] z_out
)
    cordic_hyperbolic sincos ()

    cordic_linear division ()
    
    
endmodule



