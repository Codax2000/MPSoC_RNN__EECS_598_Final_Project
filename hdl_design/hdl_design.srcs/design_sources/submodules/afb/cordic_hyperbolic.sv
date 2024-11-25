module cordic_hyperbolic#(
    parameter N = 16,
    parameter FRACTIONAL_BITS = 8,
    parameter NUM_ITERATIONS = 10
)(
    input clk, 
    input reset, 

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
    logic [$clog2(NUM_ITERATIONS+2)-1:0] count_n, count_r;

    logic [18:0] i_values [0:NUM_ITERATIONS+2];
    logic signed [N-1:0] lut [0:NUM_ITERATIONS+2];
    
    assign i_values = '{19'd1, 19'd0, 19'd1, 19'd2, 19'd3, 19'd4, 19'd4, 19'd5, 
                        19'd6, 19'd7, 19'd8, 19'd9, 19'd10};

    assign lut = '{16'sb0000000011111001, // arctanh(1-2^0-2)
                  16'sb0000000101011010, // arctanh(1-2^-1-2)
                  16'sb0000000000000000, // padding for clarity
                  16'sb0000000010001100, // arctanh(2^-1) and onwards
                  16'sb0000000001000001,
                  16'sb0000000000100000,
                  16'sb0000000000010000,
                  16'sb0000000000010000,
                  16'sb0000000000001000,
                  16'sb0000000000000100,
                  16'sb0000000000000010,
                  16'sb0000000000000001,
                  16'sb0000000000000000};
    
    
 

    logic signed [N-1:0] x_out_n, x_out_r, y_out_n, y_out_r;
    logic signed [N-1:0] z_in_n, z_in_r;

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

/*
    assign x_stage[0] = handshake_in ? 16'b0000001111000101 : x_stage[0]; // Initial x value
    assign y_stage[0] = handshake_in ? 0 : y_stage[0];                    // Initial y value
    assign z_stage[0] = handshake_in ? data_i : z_stage[0];

    cordic_hyperbolic_slice expand1 (.clk(clk), .reset(reset), .x_in(x_stage[0]), .y_in(y_stage[0]), .z_in(z_stage[0]), .i(1), .expand(1), .x_stage_out(x_stage[1]), .y_stage_out(y_stage[1]), .z_stage_out(z_stage[1]));
    cordic_hyperbolic_slice expand2 (.clk(clk), .reset(reset), .x_in(x_stage[1]), .y_in(y_stage[1]), .z_in(z_stage[1]), .i(0), .expand(1), .x_stage_out(x_stage[2]), .y_stage_out(y_stage[2]), .z_stage_out(z_stage[2]));

    cordic_hyperbolic_slice stage_0 (.clk(clk), .reset(reset), .x_in(x_stage[2]), .y_in(y_stage[2]), .z_in(z_stage[2]), .i(i_values[0]), .expand(0), .x_stage_out(x_stage[3]), .y_stage_out(y_stage[3]), .z_stage_out(z_stage[3]));
    cordic_hyperbolic_slice stage_1 (.clk(clk), .reset(reset), .x_in(x_stage[3]), .y_in(y_stage[3]), .z_in(z_stage[3]), .i(i_values[1]), .expand(0), .x_stage_out(x_stage[4]), .y_stage_out(y_stage[4]), .z_stage_out(z_stage[4]));
    cordic_hyperbolic_slice stage_2 (.clk(clk), .reset(reset), .x_in(x_stage[4]), .y_in(y_stage[4]), .z_in(z_stage[4]), .i(i_values[2]), .expand(0), .x_stage_out(x_stage[5]), .y_stage_out(y_stage[5]), .z_stage_out(z_stage[5]));
    cordic_hyperbolic_slice stage_3 (.clk(clk), .reset(reset), .x_in(x_stage[5]), .y_in(y_stage[5]), .z_in(z_stage[5]), .i(i_values[3]), .expand(0), .x_stage_out(x_stage[6]), .y_stage_out(y_stage[6]), .z_stage_out(z_stage[6]));
    cordic_hyperbolic_slice stage_4 (.clk(clk), .reset(reset), .x_in(x_stage[6]), .y_in(y_stage[6]), .z_in(z_stage[6]), .i(i_values[4]), .expand(0), .x_stage_out(x_stage[7]), .y_stage_out(y_stage[7]), .z_stage_out(z_stage[7]));
    cordic_hyperbolic_slice stage_5 (.clk(clk), .reset(reset), .x_in(x_stage[7]), .y_in(y_stage[7]), .z_in(z_stage[7]), .i(i_values[5]), .expand(0), .x_stage_out(x_stage[8]), .y_stage_out(y_stage[8]), .z_stage_out(z_stage[8]));
    cordic_hyperbolic_slice stage_6 (.clk(clk), .reset(reset), .x_in(x_stage[8]), .y_in(y_stage[8]), .z_in(z_stage[8]), .i(i_values[6]), .expand(0), .x_stage_out(x_stage[9]), .y_stage_out(y_stage[9]), .z_stage_out(z_stage[9]));
    cordic_hyperbolic_slice stage_7 (.clk(clk), .reset(reset), .x_in(x_stage[9]), .y_in(y_stage[9]), .z_in(z_stage[9]), .i(i_values[7]), .expand(0), .x_stage_out(x_stage[10]), .y_stage_out(y_stage[10]), .z_stage_out(z_stage[10]));
    cordic_hyperbolic_slice stage_8 (.clk(clk), .reset(reset), .x_in(x_stage[10]), .y_in(y_stage[10]), .z_in(z_stage[10]), .i(i_values[8]), .expand(0), .x_stage_out(x_stage[11]), .y_stage_out(y_stage[11]), .z_stage_out(z_stage[11]));
    cordic_hyperbolic_slice stage_9 (.clk(clk), .reset(reset), .x_in(x_stage[11]), .y_in(y_stage[11]), .z_in(z_stage[11]), .i(i_values[9]), .expand(0), .x_stage_out(x_stage[12]), .y_stage_out(y_stage[12]), .z_stage_out(z_stage[12]));

    assign valid_o = ps_e == eDONE;
    assign ready_o = (ps_e == eREADY) || (ps_e== eDONE && yumi_i); 

    /*
    genvar i;   

    generate
        for (i = 0; i < NUM_ITERATIONS; i = i + 1) begin
            cordic_hyperbolic_slice stage
            (
                .clk(clk),
                .reset(reset),
                .x_in(x_stage[i+1]),
                .y_in(y_stage[i+1]),
                .z_in(z_stage[i+1]),
                .i(i_values[i]), 
                .expand(0),
                .x_stage_out(x_stage[i+2]),
                .y_stage_out(y_stage[i+2]),
                .z_stage_out(z_stage[i+2])
            );

        end
    endgenerate
    """
    */
    /*
    initial begin
        lut_expand[0] = 16'b0000000011111001;
        lut_expand[1] = 16'b0000000101011010; //arctanh(1-2^-1-2)
    end
    */