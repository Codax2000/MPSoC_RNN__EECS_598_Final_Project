`timescale 1ns / 1ps
`define WIDTH 16

module cordic_mac_tb();
    logic clk, iterate;
    logic signed [`WIDTH-1:0] xin;
    logic signed [`WIDTH-1:0] yin;
    logic signed [`WIDTH-1:0] zin;
    logic signed [`WIDTH-1:0] y_f;
    logic ready_o, valid_o, rst, valid_i, yumi_i;

    integer i;

    always 
    begin
        #1
        clk = ~clk;
    end

    initial 
    begin
        clk = 0;
        iterate = 0;
        // 1.625
        xin = 16'b0011101100010110;
        yin = 16'b0001100010100011;
        // 0.5
        zin = 16'b1111101000010100;
    end

    cordic_mac_ctrl mac_ctrl
    (
        .clk_i(clk),
        .rst_i(rst),
        .data_0_i(xin),
        .data_1_i(yin),
        .data_2_i(zin),
        .valid_i(valid_i),
        .yumi_i(yumi_i),
        .data_o(y_f),
        .valid_o(valid_o),
        .ready_o(ready_o)
    );

    initial 
    begin
        @ (posedge clk)
        rst = 1;
        @ (posedge clk)
        rst = 0;
        valid_i = 1;
        #30
        yumi_i = 1;
        // 1,625
        xin = 16'b0001101000000000;
        yin = 16'b0000000000000000;
        // 0.5
        zin = 16'b0000100000000000;
        #35
        yumi_i = 0;
        valid_i = 0;
        #56
        $finish;
    end
endmodule
