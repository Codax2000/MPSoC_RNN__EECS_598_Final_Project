/*********************************************************************
*  saed_mc : SRAM_128x16 Verilog description                       *
*  ---------------------------------------------------------------   *
*  Filename      : /home/aknowlt/eecs598/project/hdl_design/pdk_mem/mc_work/SRAM_128x16.v                         *
*  SRAM name     : SRAM_128x16                                       *
*  Word width    : 16    bits                                        *
*  Word number   : 128                                               *
*  Adress width  : 7     bits                                        *
*  ---------------------------------------------------------------   *
*  Creation date : Mon December 02 2024                              *
*********************************************************************/

`timescale 1ns/100fs

`define numAddr 7
`define numWords 128
`define wordLength 16


module SRAM_128x16 (A,CE,WEB,OEB,CSB,I,O);

input 				CE;
input 				WEB;
input 				OEB;
input 				CSB;

input 	[6:0] 		A;
input 	[15:0] 	I;
output 	[15:0] 	O;

reg    	[15:0]   	memory[127:0];
reg  	[15:0]	data_out1;
reg 	[15:0] 	O;

wire 				RE;
wire 				WE;


and u1 (RE, ~CSB,  WEB);
and u2 (WE, ~CSB, ~WEB);


always @ (posedge CE) 
	if (RE)
		data_out1 = memory[A];
	else 
	   if (WE)
		memory[A] = I;
		

always @ (data_out1 or OEB)
	if (!OEB) 
		O = data_out1;
	else
		O =  16'bz;

endmodule