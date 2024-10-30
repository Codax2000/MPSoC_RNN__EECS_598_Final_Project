/**
Alex Knowlton
10/29/24

ideal memory macro with synchronous read. At positive clock, outputs data
at address addr_i. Parameters are super important, since it will look for
a file called {LAYER_NUMBER}_{MEMORY_INDEX}.mif. This serves as an early
model for a Vivado Block RAM.
*/

module mem_ideal #(
    parameter N_BITS=16,
    parameter N_ADDR=16,
    parameter LAYER_NUMBER=1,
    parameter MEMORY_INDEX=1
) (
    input logic [$clog2(N_ADDR)-1:0] addr_i,
    output logic [N_BITS-1:0] data_o,
    input logic clk_i
);

    logic [N_BITS-1:0] mem [N_ADDR-1:0];

    // synchronous read
    always_ff @(posedge clk_i)
        data_o <= mem[addr_i];

    // initialize memory
    // TODO: make this parametrized, see zyNet for reference
    initial begin
        $readmemh("test_mult.mem", mem);
    end

endmodule