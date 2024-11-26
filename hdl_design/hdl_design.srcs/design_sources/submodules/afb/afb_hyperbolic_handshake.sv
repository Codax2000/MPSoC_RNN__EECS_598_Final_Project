/*

Akash Shetty
11/21/24

Hyperbolic handshake preceding the linear division block to get the sinh cosh outputs. 

*/

module afb_hyperbolic_handshake#(
    parameter N = 16,
    parameter FRACTIONAL_BITS = 8,
    parameter NUM_ITERATIONS = 10
)(
    input clk, 
    input rst, 

    input logic signed [N-1:0] data_i, //theta 

    input logic valid_i,
    input logic yumi_i,

    output logic [1:0][N-1:0] data_o,

    output logic valid_o,
    output logic ready_o

);

    logic handshake_in, handshake_out;

    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o;

    enum logic [2:0] {eITERATE, eREADY, eDONE} ps_e, ns_e;
    logic [$clog2(NUM_ITERATIONS+2):0] count_n, count_r;

    logic [18:0] i_values [0:NUM_ITERATIONS+2];
    logic signed [N-1:0] lut [0:NUM_ITERATIONS+2];
    
    assign i_values = '{19'd1, 19'd0, 19'd1, 19'd2, 19'd3, 19'd4, 19'd4, 19'd5, 
                        19'd6, 19'd7, 19'd8, 19'd9, 19'd10};

    assign lut = '{16'sb0000000101011010, // arctanh(1-2^0-2)
                  16'sb0000000011111001, // arctanh(1-2^-1-2) 0000000101011010
                   // padding for clarity
                  16'sb0000000010001100, // arctanh(2^-1) and onwards
                  16'sb0000000001000001,
                  16'sb0000000000100000,
                  16'sb0000000000010000,
                  16'sb0000000000010000,
                  16'sb0000000000001000,
                  16'sb0000000000000100,
                  16'sb0000000000000010,
                  16'sb0000000000000001,
                  16'sb0000000000000000,
                  16'sb0000000000000000};
    
    
 

    logic signed [N-1:0] x_out_n, x_out_r, y_out_n, y_out_r;
    logic signed [N-1:0] z_in_n, z_in_r;
    
    logic signed [N-1:0] y_shift_e, y_shift;
    logic signed [N-1:0] x_shift_e, x_shift;

    assign x_shift_e = (x_out_r - (x_out_r >>> (i_values[count_r] + 2)));
    assign x_shift = x_out_r >>> i_values[count_r];

    assign y_out_n = handshake_in ? '0 : 
                    ps_e != eITERATE ? y_out_r : 
                    count_r < 2 ?
                    z_in_r[N-1] ? y_out_r - (x_shift_e) :
                                 y_out_r + (x_shift_e):
                    z_in_r[N-1] ? y_out_r - (x_shift) :
                                 y_out_r + (x_shift);

    assign z_in_n = handshake_in ? data_i : 
                    ps_e != eITERATE ? z_in_r : 
                    (count_r < 2 ?
                    (z_in_r[N-1] ? z_in_r + lut[count_r] :
                                 z_in_r - lut[count_r]) :
                    (z_in_r[N-1] ? z_in_r + lut[count_r] :
                                 z_in_r - lut[count_r]));

    
    assign y_shift_e = (y_out_r - (y_out_r >>> (i_values[count_r] + 2)));
    assign y_shift = y_out_r >>> i_values[count_r];

    assign x_out_n = handshake_in ? 16'b0000001111000101: 
                    ps_e != eITERATE ? x_out_r : 
                    count_r < 2 ?
                    z_in_r[N-1] ? x_out_r - (y_shift_e) :
                                 x_out_r + (y_shift_e):
                    z_in_r[N-1] ? x_out_r - (y_shift):
                                 x_out_r + (y_shift);



    assign valid_o = (ps_e == eDONE);                    
    assign ready_o = (ps_e == eREADY) || (ps_e == eDONE && yumi_i);
    

    always_comb begin
        case (ps_e)
            eREADY: begin
                ns_e = valid_i ? eITERATE : eREADY;
                count_n = '0;
            end
            eITERATE: begin
                ns_e = (count_r == (NUM_ITERATIONS+2)) ? eDONE : eITERATE;
                count_n = count_r + 1;
            end
            eDONE: begin
                ns_e =  !yumi_i ? eDONE : 
                        valid_i ? eITERATE : eREADY;
                count_n = 0;
            end
            default: begin
                ns_e = eREADY;
                count_n = count_r;
            end
        endcase
    end

    assign data_o[0] = y_out_r;
    assign data_o[1] = x_out_r;

    // Sequential logic for state transitions

    always_ff @(posedge clk or negedge rst) begin
        if (~rst) begin
            z_in_r <= '0;
            ps_e <= eREADY;
            x_out_r <= '0;
            y_out_r <= '0;
            count_r <= '0;
        end else begin
            z_in_r <= z_in_n;
            ps_e <= ns_e;
            x_out_r <= x_out_n;
            y_out_r <= y_out_n;
            count_r <= count_n;
        end
    end

endmodule
