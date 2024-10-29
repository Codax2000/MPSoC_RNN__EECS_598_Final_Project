module mac_ideal #(
    parameter N_x = 16, // N and R for fractional bits
    parameter R_x = 8,
    parameter N_mem = 16,
    parameter R_mem = 8,
    parameter N_out = 16,
    parameter R_out = 8
) (
    input logic [N_x-1:0] data_i,
    input logic [N_mem-1:0] mem_i,
    input logic clk_i,
    input logic rstb_i,
    output logic [N_out-1:0] data_o
);

    // todo implement simple MAC
    
endmodule