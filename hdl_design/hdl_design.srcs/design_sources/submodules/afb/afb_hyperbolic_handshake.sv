module afb_hyperbolic_handshake #(
    parameter N = 16,
    parameter FRACTIONAL_BITS = 8,
    parameter NUM_ITERATIONS = 10
)(
    input clk, 
    input reset, 

    input logic signed [N-1:0] data_i, 
    input logic valid_i,
    input logic yumi_i,

    output logic [1:0][N-1:0] data_o,
    output logic valid_o,
    output logic ready_o

);

    logic hanshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;

    enum logic [2:0] {eITERATE, eREADY, eDONE} ps_e, ns_e;
    logic [$clog2(NUM_ITERATIONS)-1:0] count_n, count_r;

    logic [0:NUM_ITERATIONS+2][3:0] i_values;

    always_comb begin
        i_values[0] = 1;
        i_values[1] = 0;
        i_values[2] = 1;
        i_values[3] = 2;
        i_values[4] = 3;
        i_values[5] = 4;
        i_values[6] = 4;
        i_values[7] = 5;
        i_values[8] = 6;
        i_values[9] = 7;
        i_values[10] = 8;
        i_values[11] = 9;
        i_values[12] = 10;
    end

    logic signed [N-1:0] lut [0:NUM_ITERATIONS+2];

    always_comb begin
        lut[0] = 16'b0000000011111001;
        lut[1] = 16'b0000000101011010; //arctanh(1-2^-1-2)
        lut[2] = 16'b0000000000000000;
        lut[3] = 16'b0000000010001100; // arctanh(2^-1)
        lut[4] = 16'b0000000001000001;
        lut[5] = 16'b0000000000100000;
        lut[6] = 16'b0000000000010000;
        lut[7] = 16'b0000000000010000;
        lut[8] = 16'b0000000000001000;
        lut[9] = 16'b0000000000000100;
        lut[10] = 16'b0000000000000010;
        lut[11] = 16'b0000000000000001;
        lut[12] = 16'b0000000000000000;
    end
    

    logic signed [N-1:0] x_out_n, x_out_r, y_out_n, y_out_r;
    logic signed [N-1:0] z_in_n, z_in_r;
    logic signed [N-1:0] iterate;
    
    // cordic hyperbolic
    assign x_out_n = handshake_in ? 16'b0000001111000101: 
                    ps_e != eITERATE ? x_out_r :
                    (count_r < 2 ?
                    (z_in_r[N-1] ? x_out_r + (y_out_r - (y_out_r >>> (i_values[count_r] + 2))) :
                                 x_out_r - (y_out_r - (y_out_r >>> (i_values[count_r] + 2)))) :
                    (z_in_r[N-1] ? x_out_r + (y_out_r >>> i_values[count_r]) :
                                 x_out_r - (y_out_r >>> i_values[count_r])));
                    

    assign y_out_n = handshake_in ? '0 : 
                    ps_e != eITERATE ? y_out_r : 
                    (count_r < 2 ?
                    (z_in_r[N-1] ? y_out_r + (x_out_r - (x_out_r >>> (i_values[count_r] + 2))) :
                                 y_out_r - (x_out_r - (x_out_r >>> (i_values[count_r] + 2)))) :
                    (z_in_r[N-1] ? y_out_r + (x_out_r >>> i_values[count_r]) :
                                 y_out_r - (x_out_r >>> i_values[count_r])));

    assign z_in_n = handshake_in ? data_i : 
                    ps_e != eITERATE ? z_in_r : 
                    (count_r < 2 ?
                    (z_in_r[N-1] ? z_in_r - lut[count_r] :
                                 z_in_r + lut[count_r]) :
                    (z_in_r[N-1] ? z_in_r - lut[count_r] :
                                 z_in_r + lut[count_r]));

    assign valid_o = (ps_e == eDONE);                    
    assign ready_o = (ps_e == eREADY) || handshake_out;
    
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
                count_n = count_r;
            end
            default: begin
                ns_e = eREADY;
                count_n = count_r;
            end
        endcase
    end

    assign data_o[0] = x_out_r;
    assign data_o[1] = y_out_r;

    // Sequential logic for state transitions

    always_ff @(posedge clk or negedge reset) begin
        if (~reset) begin
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