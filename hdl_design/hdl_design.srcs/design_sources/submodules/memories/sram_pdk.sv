module sram_pdk (
    input logic [6:0] addr_i,
    output logic [15:0] data_o,
    input logic clk_i
);

    SRAM_128x16 mem (
        .CE(clk_i),
        .WEB(1'b1),
        .OEB(1'b0),
        .CSB(1'b1),

        .A(addr_i),
        .I(16'h0000),
        .O(data_o)
    );

endmodule
