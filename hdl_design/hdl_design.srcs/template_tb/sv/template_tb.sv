module template_tb();

    // N: Number of bits in a word
    parameter N=16;
    
    // L1: Number of words in input
    parameter L1=1;
    
    // L2: Number of words in output
    parameter L2 = 1;
    
    // T: Number of testcases
    parameter T = 10;
    
    // declare variables for DUT
    logic valid_i, ready_o, yumi_i, valid_o;
    logic [L1-1:0][N-1:0] data_i;
    logic [L2-1:0][N-1:0] data_o, expected_data_o;
    logic rstb_i, clk_i;
    
    // create send and receive modules locally
    // create DUT
    relu_afb #(.N(N)) DUT(.*);
    
    // create memories for input/output values and initialize them
    logic [L1-1:0][N-1:0] input_test_vals [T-1:0];
    logic [L2-1:0][N-1:0] output_test_vals [T-1:0];
    
    initial begin
        $readmemh("relu_input.mem", input_test_vals);
        $readmemh("relu_output.mem", output_test_vals);
    end
    
    // counters for input/output addresses
    logic [$clog2(T)-1:0] input_counter_n, input_counter_r;
    logic [$clog2(T)-1:0] output_counter_n, output_counter_r;
    
    // declare variables for debugging more easily;
    logic handshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;
    
    // next address counter assignment
    assign input_counter_n = (valid_i && ready_o) && (input_counter_r != T) ? 
        input_counter_r + 1 : input_counter_r;
    assign output_counter_n = valid_o && yumi_i && (output_counter_r != T) ? 
        output_counter_r + 1 : output_counter_r;
    
    // Create an LFSR to assign other two ready and valid signals
    // this makes things more robust, since ready/valid should be independent of each other
    logic [3:0] lfsr_n, lfsr_r;
    assign lfsr_n = {lfsr_r[0]^lfsr_r[3], lfsr_r[3:1]};
    assign yumi_i = lfsr_r[0] && (output_counter_r != T);
    assign valid_i = lfsr_r[2] && (input_counter_r != T);
    
    // assign input and expected data from memories
    assign data_i = input_test_vals[input_counter_r];
    assign expected_data_o = output_test_vals[output_counter_r];
    
    // create clock
    parameter CLOCK_PERIOD = 10;
    initial begin
        clk_i = 1'b0;
        forever #(CLOCK_PERIOD / 2) clk_i = ~clk_i;
    end
    
    // reset the circuit
    initial begin
        rstb_i = 1'b0;
        #(5 * CLOCK_PERIOD) rstb_i = 1'b1;
    end
    
    integer fd;
    initial begin
        // Note: this csv file is for later analysis only and is a convenient wavedump,
        // but is in the sim directory, so not super useful
        fd = $fopen("output.csv", "w");
        $fwrite(fd, "test_index,expected,received\n");
        forever begin
            @(negedge clk_i); // wait for the negative edge of the clock
            
            // reasoning: if the output counter has gone all the way up, we are done
            // sending data and can do final checks
            // should be able to check that valid_o is low
            if (output_counter_r == T) begin
                $fclose(fd);
                $stop;
            end else if (valid_o && yumi_i) begin
                assert (expected_data_o == data_o)
                    $display("Testcase %d passed", output_counter_r + 2'b01);
                else
                    $display("Testcase %d failed: Expected %h, Received %h", output_counter_r+2'b01, expected_data_o, data_o);
                $fwrite(fd,"%u,%d,%d\n", output_counter_r,expected_data_o,data_o);
            end
        end
    end
    
    // update counters and LFSR at the clock
    always_ff @(posedge clk_i) begin
        if (~rstb_i) begin
            input_counter_r <= '0;
            output_counter_r <= '0;
            lfsr_r <= 4'hF;
        end else begin
            input_counter_r <= input_counter_n;
            output_counter_r <= output_counter_n;
            lfsr_r <= lfsr_n;
        end
    end
endmodule
