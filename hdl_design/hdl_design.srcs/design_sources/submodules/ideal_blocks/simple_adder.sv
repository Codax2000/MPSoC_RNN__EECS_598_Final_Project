/**
Alex Knowlton

Synchronous adder: at positive clock edge, latches the sum of a_i and b_i with one extra
bit to avoid overflow.

Inputs:
    a_i, b_i: N_BITS long, signed input values
    clk_i: input clock
    rstn_i: active low reset

Output:
    sum_o: N_BITS+1 long, signed sum of a_i and b_i
*/
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
            sum_o <= {{N_BITS+1}{1'b0}};
        else
            sum_o <= sum_n;
    end
    
endmodule
