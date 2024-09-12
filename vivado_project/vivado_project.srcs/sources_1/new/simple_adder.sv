`timescale 1ns / 1ps

module simple_adder #(parameter N_BITS=16)(
    input  logic signed [N_BITS-1:0] a_i,
    input  logic signed [N_BITS-1:0] b_i,
    output logic signed [N_BITS:0] sum_o,
    input clk_i,
    input rstn_i
    );
    
    logic [N_BITS:0] sum_n;
    assign sum_n = a_i + b_i;
    
    always_ff @(posedge clk_i) begin
        if (~rstn_i)
            sum_o <= 17'h0_0000;
        else
            sum_o <= sum_n;
    end
    
endmodule
