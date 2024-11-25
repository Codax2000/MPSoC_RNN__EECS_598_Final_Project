`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/21/2024 01:45:33 PM
// Design Name: 
// Module Name: cordic_afb_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module cordic_afb_tb();

    parameter WIDTH = 16;

    logic clk, rst;
    logic afb_mode;

    logic signed [WIDTH - 1:0] x_in;
    logic signed [WIDTH - 1:0] y_in;
    logic signed [WIDTH - 1:0] z_in;
    logic signed [WIDTH - 1:0] x_out;
    logic signed [WIDTH - 1:0] y_out;
    logic signed [WIDTH - 1:0] z_out;

    cordic_afb afb_test(
        .clk(clk),
        .reset(reset),
        .afb_mode(afb_mode),
        .x_in(x_in),
        .y_in(y_in),
        .z_in(z_in),
        .x_out(x_out),
        .y_out(y_out),
        .z_out(z_out)
    );

    always #1 clk = ~clk;

    initial begin
        clk = 0;
        rst = 1;

        #5;

        rst = 0;


        //test case 1 Tanh -1
        afb_mode = 1;
        x_in = 16'b0000001111000101;
        y_in = 0;
        z_in = 16'b1111111100000000;
        #100;
        //test case 2 sigmoid -1
        afb_mode = 0;
        x_in = 16'b0000001111000101;
        y_in = 0;
        z_in = 16'b1111111100000000;
        #100;
        //test case 3 tanh -3
        afb_mode = 1;
        x_in = 16'b0000001111000101;
        y_in = 0;
        z_in = 16'b1111110100000000;
        #100;
        //test case 4 sigmoid -3
        afb_mode = 0;
        x_in =  16'b0000001111000101;
        y_in = 0;
        z_in = 16'b1111110100000000;
        #100;

        $stop;
    end
   
endmodule




