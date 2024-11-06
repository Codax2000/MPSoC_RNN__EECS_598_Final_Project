`timescale 1ns / 1ps
`define WIDTH 16

module template_tb();
    logic clk, rst;
    logic signed [`WIDTH-1:0] xin;
    logic signed [`WIDTH-1:0] yin;
    logic signed [`WIDTH-1:0] zin;
    logic signed [`WIDTH-1:0] y_f;

    integer i;

    always 
    begin
        #1
        clk = ~clk;
    end

    initial 
    begin
        clk = 0;
        rst = 1;
        // 1.625
        xin = 16'b0011101100010110;
        yin = 16'b0001100010100011;
        // 0.5
        zin = 16'b1111101000010100;
    end

    cordic_mac mac
    (
        .clk_i(clk),
        .rst_i(rst),
        .xin_i(xin),
        .yin_i(yin),
        .zin_i(zin),
        .y_o(y_f)
    );

    initial 
    begin
        @ (posedge clk)
        rst = 1;
        @ (posedge clk)
        rst = 0;
        #40
        $finish;
    end
endmodule
