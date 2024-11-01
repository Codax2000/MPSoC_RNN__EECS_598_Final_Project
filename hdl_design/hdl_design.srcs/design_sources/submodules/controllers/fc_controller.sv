/**
Alex Knowlton
10/29/2024

General controller for fully-connected layer. Arranges input handshakes and
memory addresses, and also instantiates memory array. Handshakes directly with
the MAC cell. Note: this also deals with sending the bias to the MAC cell,
so the toplevel layer module doesn't have to, but it will not be available
for an input handshake during that time.

Input handshake:
data_i, valid_i, ready_o - standard
    data_i: N_BITS_DATA bits long, signed value

Output handshake:
data_o, valid_o, yumi_i - standard signals

Globals:
    clk_i - input clock
    rstb_i - active low reset

Note: data_o is represented as a packed array arranged as {input X value, memory outputs}
*/

module fc_controller #(
    parameter LAYER_NUMBER=1,
    parameter N_INPUTS=16,
    parameter N_OUTPUTS=16,
    parameter N_BITS_MEM=16,
    parameter N_BITS_DATA=16,
    parameter R_BITS_DATA=8
) (
    input logic [N_BITS_DATA-1:0] data_i,
    input logic valid_i,
    output logic ready_o,

    output logic [(N_BITS_DATA+N_OUTPUTS*N_BITS_MEM)-1:0] data_o,
    input logic yumi_i,
    output logic valid_o,

    input logic rstb_i,
    input logic clk_i
);

    enum logic [1:0] {eREADY, eFULL, eBIAS} ps_e, ns_e;
    localparam logic [N_BITS_DATA-1:0] ONE = (1 << (R_BITS_DATA));
    logic handshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;

    logic [$clog2(N_INPUTS)-1:0] addr_r, addr_n;
    logic [N_OUTPUTS-1:0][N_BITS_MEM-1:0] mem_data_lo;
    logic [N_BITS_DATA-1:0] data_i_r, data_i_n;

    // assign outputs and registers
    assign valid_o = (ps_e == eBIAS) || (ps_e == eFULL);
    assign data_o = ps_e == eBIAS ? {ONE, mem_data_lo} : {data_i_r, mem_data_lo};
    assign data_i_n = handshake_in ? data_i : data_i_r;

    // next state logic
    always_comb begin
        case (ps_e)
            eREADY: begin
                ready_o = 1'b1;
                ns_e = handshake_in ? eFULL : eREADY;
                addr_n = addr_r;
            end
            eFULL: begin
                ready_o = handshake_out && (addr_r != N_INPUTS - 1);
                ns_e = (~handshake_out) ? eFULL :
                       (addr_r == N_INPUTS - 1) ? eBIAS : 
                       (handshake_in) ? eFULL: eREADY;
                addr_n = handshake_out ? addr_r + 2'b01 : addr_r; 
            end
            eBIAS: begin
                ready_o = handshake_out;
                addr_n = handshake_out ? 0 : addr_r;
                ns_e = (~handshake_out) ? eBIAS :
                       (handshake_in) ? eFULL : eREADY;
            end
            default: begin
                ready_o = 1'b1;
                ns_e = handshake_in ? eFULL : eREADY;
                addr_n = addr_r;
            end
        endcase
    end

    // sequential block
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            addr_r <= '0;
            data_i_r <= '0;
            ps_e <= eREADY;
        end else begin
            addr_r <= addr_n;
            data_i_r <= data_i_n;
            ps_e <= ns_e;
        end
    end

    // instantiate memory
    mem_array #(
        .N_BITS(N_BITS_MEM),
        .LAYER_NUMBER(LAYER_NUMBER),
        .ARRAY_LENGTH(N_OUTPUTS),
        .N_WEIGHTS(N_INPUTS+1)
    ) memories (
        .addr_i(addr_n),
        .clk_i,
        .data_o(mem_data_lo)
    );

endmodule