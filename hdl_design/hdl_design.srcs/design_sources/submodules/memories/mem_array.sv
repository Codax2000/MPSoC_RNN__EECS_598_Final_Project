/**
Alex Knowlton
10/29/24

ideal memory array macro with synchronous read. Simply initializes an array
of memories that all share the same address and outputs the result as a packed
array.
*/
module mem_array #(
    parameter N_BITS=16,
    parameter LAYER_NUMBER=1,
    parameter ARRAY_LENGTH=16,
    parameter N_WEIGHTS=16
) (
    input logic [$clog2(N_WEIGHTS)-1:0] addr_i,
    input logic clk_i,
    input logic rstb_i,
    output logic [ARRAY_LENGTH-1:0][N_BITS-1:0] data_o
);

    genvar i;
    generate
        for (i = 0; i < ARRAY_LENGTH; i = i + 1) begin
            // `ifdef VIVADO
            // ROM_inferred #(
            //     .N_BITS(N_BITS),
            //     .N_ADDR(N_WEIGHTS),
            //     .LAYER_NUMBER(LAYER_NUMBER),
            //     .MEMORY_INDEX(i)
            // ) mem (
            //     .addr_i,
            //     .clk_i,
            //     .rstb_i,
            //     .data_o(data_o[i])
            // );
            // `endif
            // `ifndef VIVADO
            mem_ideal #(
                .N_BITS(N_BITS),
                .N_ADDR(N_WEIGHTS),
                .LAYER_NUMBER(LAYER_NUMBER),
                .MEMORY_INDEX(i)
            ) mem (
                .addr_i,
                .clk_i,
                .data_o(data_o[i])
            );
            // `endif
        end
    endgenerate

endmodule