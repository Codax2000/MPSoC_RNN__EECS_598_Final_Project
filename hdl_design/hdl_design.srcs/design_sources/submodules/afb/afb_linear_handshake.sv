module afb_linear_handshake #(
    parameter N=16,
    parameter R=12,
    parameter logic IS_TANH=1,
    parameter N_ITERATIONS=13
) (
    input logic [1:0][N-1:0] data_i, // theta
    input logic valid_i,
    output logic ready_o,

    output logic [N-1:0] data_o,
    output logic valid_o,
    input logic yumi_i,

    input logic clk_i,
    input logic rstb_i
);

    logic handshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;

    enum logic [1:0] {eREADY, eITERATE, eDONE} ps_e, ns_e;
    logic [$clog2(N_ITERATIONS+1)-1:0] count_n, count_r;

    // CORDIC logic
    logic signed [N-1:0] x_in_n, x_in_r, y_in_n, y_in_r, x_shift;
    logic signed [N-1:0] data_n, data_r, one_shift;
    localparam logic signed [N-1:0] ONE = 1 << R;
    assign x_shift = x_in_r >>> count_r;
    assign one_shift = ONE >>> count_r;
    assign x_in_n = handshake_in ? data_i[1] : x_in_r;
    assign y_in_n = handshake_in ? data_i[0] : 
                    ps_e != eITERATE ? y_in_r : 
                    y_in_r[N-1] ? y_in_r + x_shift : y_in_r - x_shift;
    assign data_n = handshake_in ? '0 :
                    ps_e != eITERATE ? data_r :
                    y_in_r[N-1] ? data_r - one_shift : data_r + one_shift;

    // output logic
    assign valid_o = ps_e == eDONE;
    assign ready_o = ps_e == eREADY || (ps_e == eDONE && yumi_i);

    // next state logic
    always_comb begin
        case(ps_e)
            eREADY: begin
                ns_e = valid_i ? eITERATE : eREADY;
                count_n = valid_i ? 1 : 0;
            end
            eITERATE: begin
                ns_e = count_r == (N_ITERATIONS) ? eDONE : eITERATE;
                count_n = count_r + 1;
            end
            eDONE: begin
                ns_e =  !yumi_i ? eDONE : 
                        valid_i ? eITERATE : eREADY;
                count_n = !yumi_i ? count_r : 
                    valid_i ? 1 : 0;
            end
            default: begin
                ns_e = eREADY;
                count_n = count_r;
            end
        endcase
    end

    assign data_o = IS_TANH ? data_r : (data_r + ONE) >>> 1;

    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            data_r <= '0;
            ps_e <= eREADY;
            x_in_r <= '0;
            y_in_r <= '0;
            count_r <= '0;
        end else begin
            data_r <= data_n;
            ps_e <= ns_e;
            x_in_r <= x_in_n;
            y_in_r <= y_in_n;
            count_r <= count_n;
        end
    end

endmodule