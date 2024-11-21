module cordic_afb(
    input clk, 
    input reset, 
    input lut_hyperbolic,
    input tanh, 
    input afb_mode, // 1 for tanh 0 for sigmoid
    input signed [15:0] x_in,
    input signed [15:0] y_in,
    input signed [15:0] z_in,
    output logic signed [15:0] x_out
    output logic signed [15:0] y_out
    output logic signed [15:0] z_out
)

    logic signed [15:0] x_hyper_out, y_hyper_out, z_hyper, out;

    cordic_hyperbolic sincos (
        .clk(clk),
        .reset(reset),
        .x_in(x_in),
        .y_in(y_in),
        .z_in(z_in),
        .x_out(x_hyper_out),
        .y_out(y_hyper_out),
        .z_out(z_hyper_out)
    );

    cordic_linear division (
        .clk(clk),
        .reset(reset),
        .x_in(x_hyper_out),
        .y_in(y_hyper_out),
        .z_in(z_hyper_out),
        .x_out(x_out),
        .y_out(y_out),
        .z_out(z_out)
    );
    
    
    
endmodule



