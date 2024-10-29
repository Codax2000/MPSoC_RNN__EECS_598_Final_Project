`timescale 1ns / 1ps
/**
Alex Knowlton

Testbench for simple adder, which serves to ensure Vivado is running correctly.
*/
module simple_adder_tb();

    logic [7:0] a_i, b_i;
    logic [8:0] sum_o;
    logic clk_i, rstn_i;
    
    simple_adder #(.N_BITS(8)) DUT (.*);
    
    localparam CLOCK_PERIOD = 100;
    initial begin
        clk_i = 1'b0;
        forever #(CLOCK_PERIOD / 2) clk_i = ~clk_i;
    end
    
    initial begin
        rstn_i = 0;
        a_i = 8'h04;
        b_i = 8'h03; @(posedge clk_i);
        @(negedge clk_i);
        rstn_i = 1'b1;
        
        repeat(2) @(posedge clk_i);
        @(negedge clk_i) begin
            a_i = 8'h01;
            b_i = 8'hFF;
        end
        repeat(3) @(posedge clk_i);
        $stop;
        
    end
endmodule
