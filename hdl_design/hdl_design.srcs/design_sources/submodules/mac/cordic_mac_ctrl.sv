module cordic_mac_ctrl
#(
    parameter WIDTH = 16,
    parameter FRACTIONAL_BITS = 12
)
(
    input logic clk_i,
    input logic rst_i,
    input logic signed [WIDTH-1:0] data_0_i,
    input logic signed [WIDTH-1:0] data_1_i,
    input logic signed [WIDTH-1:0] data_2_i,
    input logic valid_i,
    input logic yumi_i,
    output logic signed [WIDTH-1:0] data_o,
    output logic valid_o,
    output logic ready_o
);

    enum logic [2:0] {READY, ITERATE, SAMPLE, SAMPLE2, DONE} curr_state, next_state; // TODO Add extra state SAMPLE

    logic signed [WIDTH-1:0] xin;
    logic signed [WIDTH-1:0] yin;
    logic signed [WIDTH-1:0] zin;
    logic signed [WIDTH-1:0] sum;
    logic unsigned [3:0] count;
    logic iterate;
    logic sample_input;

    cordic_mac mac(
        .clk_i(clk_i),
        .iterate(iterate),
        .xin_i(xin),
        .yin_i(yin),
        .zin_i(zin),
        .sample_input(sample_input),
        .y_o(sum),
        .ready_o(ready_o)
        );
    
    always_ff @ (posedge clk_i)
    begin
        if (rst_i)
        begin
            curr_state <= READY;
        end
        
        else
        begin
            curr_state <= next_state;
        end
    end

    // Counter process
    always_ff @ (posedge clk_i)
    begin
        if (iterate == 1'b1)
            count <= count + 1'b1;
        else
            count <= 4'd0;

        // Add another state to clock in input?
        if (sample_input == 1'b1)
        begin
            xin <= data_0_i;
            yin <= data_1_i;
            zin <= data_2_i;
        end

        else
        begin
            xin <= xin;
            yin <= yin;
            zin <= zin;
        end
    end

    always_comb
    begin
        next_state = curr_state;
        // State Transitions
        unique case (curr_state)
            READY:
            begin
                // Create internal signal and check mac ready_o instead of iterate?
                if (valid_i && iterate == 1'b0)
                    next_state = SAMPLE;
                else
                    next_state = READY;
            end

            SAMPLE:
            begin
                next_state = SAMPLE2;
            end

            SAMPLE2:
            begin
                next_state = ITERATE;
            end

            ITERATE:
            begin
                // Continue to iterate until CORDIC is done (maybe use internal ready)
                if (count == 4'd12)
                    next_state = DONE;
                else
                    next_state = ITERATE;
            end

            DONE:
            begin
                // Wait for ACK
                if (yumi_i)
                    next_state = READY;
                else
                    next_state = DONE;
            end
            default :
                next_state = READY;
        endcase
    end

    always_comb
    begin
        case (curr_state)
            READY:
            begin
                data_o = 1'b0; // I think ?
                valid_o = 1'b0;
                iterate = 1'b0;
                sample_input = 1'b0;
                // ready_o outputted already by CORDIC MAC
            end

            SAMPLE:
            begin
                data_o = 1'b0;
                valid_o = 1'b0;
                iterate = 1'b0;
                sample_input = 1'b1;
            end

            SAMPLE2:
            begin
                data_o = 1'b0;
                valid_o = 1'b0;
                iterate = 1'b0;
                sample_input = 1'b1;
            end

            ITERATE:
            begin
                data_o = 1'b0; // I think ?
                valid_o = 1'b0;
                iterate = 1'b1;
                sample_input = 1'b0;
                // ready_o outputted already by CORDIC MAC
            end

            DONE:
            begin
                data_o = sum; // I think ?
                valid_o = 1'b1;
                iterate = 1'b0;
                sample_input = 1'b0;
                // ready_o outputted already by CORDIC MAC
            end
        endcase
    end


endmodule
