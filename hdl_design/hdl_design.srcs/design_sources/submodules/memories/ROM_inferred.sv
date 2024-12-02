`ifndef SYNOPSIS
`define VIVADO
`endif
/**
Alex Knowlton
4/12/2023

Inferred block RAM using Xylinx Vivado.
*/

`ifdef VIVADO
module ROM_inferred #(
    parameter N_BITS=8,
    parameter N_ADDR=8,
    parameter LAYER_NUMBER=4,
    parameter MEMORY_INDEX=1
) (
    input logic [$clog2(N_ADDR)-1:0] addr_i,
    output logic [N_BITS-1:0] data_o,
    input logic clk_i,
    input logic rstb_i
);
    localparam logic [7:0] zero = 8'h30;
    localparam logic [7:0] ones = zero + (MEMORY_INDEX % 10);
    localparam logic [7:0] tens = zero + ((MEMORY_INDEX / 10) % 10);
    localparam logic [7:0] hundreds = zero + (MEMORY_INDEX / 100);
    localparam logic [31:0] extension = ".mem";
    localparam logic [71:0] MEM_INIT = {zero+LAYER_NUMBER, 8'h5f, hundreds, tens, ones, extension};

    xpm_memory_sprom #(
        .ADDR_WIDTH_A($clog2(N_ADDR)),              // DECIMAL
        .MEMORY_INIT_FILE(MEM_INIT),     // String
        .MEMORY_OPTIMIZATION("true"),  // String
        .MEMORY_PRIMITIVE("block"),     // String
        .MEMORY_SIZE(N_ADDR*N_BITS),            // DECIMAL
        .MESSAGE_CONTROL(0),           // DECIMAL
        .READ_DATA_WIDTH_A(N_BITS),        // DECIMAL
        .READ_LATENCY_A(1),            // DECIMAL
        .READ_RESET_VALUE_A("0"),      // String
        .RST_MODE_A("SYNC"),           // String
        .SIM_ASSERT_CHK(0),            // DECIMAL; 0=disable simulation messages, 1=enable simulation messages
        .USE_MEM_INIT(1),              // DECIMAL
        .USE_MEM_INIT_MMI(0),          // DECIMAL
        .WAKEUP_TIME("disable_sleep")  // String
    )
    xpm_memory_sprom_inst (
        .douta(data_o),                   // READ_DATA_WIDTH_A-bit output: Data output for port A read operations.
        .addra(addr_i),                   // ADDR_WIDTH_A-bit input: Address for port A read operations.
        .clka(clk_i),                     // 1-bit input: Clock signal for port A.
        .ena(1'b1),                       // 1-bit input: Memory enable signal for port A. Must be high on clock
                                        // cycles when read operations are initiated. Pipelined internally.
        .rsta(~rstb_i),                     // 1-bit input: Reset signal for the final port A output register stage.
                                        // Synchronously resets output port douta to the value specified by
                                        // parameter READ_RESET_VALUE_A.
        .injectsbiterra(1'b0),
        .injectdbiterra(1'b0),
        .regcea(1'b1),
        .sleep(1'b0)
    );

endmodule
`endif
