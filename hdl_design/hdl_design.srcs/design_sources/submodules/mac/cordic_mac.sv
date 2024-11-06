module cordic_mac
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 12
)
(
    input logic clk_i,
    input logic rst_i,
    input logic signed [WIDTH-1:0] xin_i,
    input logic signed [WIDTH-1:0] yin_i,
    input logic signed [WIDTH-1:0] zin_i,
    output logic signed [WIDTH-1:0] y_o
);

    logic signed [1:0] dir [FRACTIONAL_BITS];
    logic signed [WIDTH-1:0] y;
    logic signed [WIDTH-1:0] x_reg;
    logic signed [4:0] j;

    genvar i;
    generate
        assign dir[0] = (zin_i[WIDTH - 1] == 1'b1) ? 2'd1 : -2'd1;
        for (i = 1; i < FRACTIONAL_BITS; i++)
        begin
            always_comb 
            begin
                if (zin_i[FRACTIONAL_BITS - i] == 1'b0) 
                    dir[i] = 2'd01; // +1 in signed 2-bit representation
                else 
                    dir[i] = -2'd01; // -1 in signed 2-bit representation
            end
        end
    endgenerate


    always_ff @ (posedge clk_i) 
    begin
        if (rst_i)
        begin
            j <= 5'd0;
            y <= yin_i;
        end

        else
        begin
            if (j < FRACTIONAL_BITS)
            begin
                y <= y + x_reg;
                j <= j + 5'd1;
            end
            
            else
            begin
                y_o <= y;
            end
        end
    end

    always_comb
    begin
        if (dir[j] == 2'b01)
        begin
            x_reg <= $signed(~(xin_i >> (j + 5'd1)) + 16'd1);
        end

        else
        begin
            x_reg <= $signed(xin_i >> (j + 5'd1));
        end
    end

endmodule