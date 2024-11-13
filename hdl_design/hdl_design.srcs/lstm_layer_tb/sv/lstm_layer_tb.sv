`ifndef SYNOPSIS
`define VIVADO
`timescale 1ns/10ps
`endif

/**
Alex Knowlton
10/29/2024

Testbench template lightly based on UVM and BaseJump SystemVerilog coding standards.
Assumes a module with helpful valid/ready interfaces at both ends and sends data from
a .mem file generated externally. Compares to another .mem file generated externally
and runs assertion testing on the comparison.

Assumes the following input and output to the DUT:
Input handshake:
logic valid_i, ready_o;
logic [L1-1:0][N-1:0] data_i;

Output handshake:    
logic yumi_i, valid_o;
logic [L2-1:0][N-1:0] data_o, expected_data_o;

Global clock and sync reset (active low)
logic rstb_i, clk_i;

You should define the following variables based on external Matlab/Python simulations:
N1 - number of bits in an input word
N2 - number of bits in an output word
R1 - number of fractional bits in input word
R2 - number of fractional bits in output word
L1 - number of words in input array
L2 - number of words in output array
T1 - number of values to send into DUT
T2 - number of values to receive from DUT

Instantiate the DUT, you should only have to declare parameters and then connect using DUT (.*)
*/

module lstm_layer_tb();

    // Define fixed-point values
    parameter N1 = 16;
    parameter N2 = 16;
    parameter R1 = 8;
    parameter R2 = 8;
    
    // L1: Number of words in input
    parameter L1 = 1;
    
    // L2: Number of words in output
    parameter L2 = 1;
    
    // T1: Number of value to send to DUT
    parameter T1 = 32;
    
    // T2: Number of values we expect to receive from DUT
    parameter T2 = 32;
    
    // declare variables for DUT
    logic valid_i, ready_o, yumi_i, valid_o;
    logic [L1-1:0][N1-1:0] data_i;
    logic [L2-1:0][N2-1:0] data_o, expected_data_o;
    logic rstb_i, clk_i;
    
    // create send and receive modules locally
    // create DUT
    lstm_layer DUT(.*);
    
    // create memories for input/output values and initialize them
    logic [L1-1:0][N1-1:0] input_test_vals [T1-1:0];
    logic [L2-1:0][N2-1:0] output_test_vals [T2-1:0];
    
    initial begin
	`ifdef VIVADO
        $readmemh("lstm_input.mem", input_test_vals);
        $readmemh("lstm_output.mem", output_test_vals);
	`else
	    $readmemh("./hdl_design/hdl_design.srcs/template_tb/mem/relu_input.mem", input_test_vals);
	    $readmemh("./hdl_design/hdl_design.srcs/template_tb/mem/relu_output.mem", output_test_vals);
	`endif
    end
    
    // **************** DO NOT EDIT BELOW THIS LINE ******************
    
    // counters for input/output addresses
    logic [$clog2(T1):0] input_counter_n, input_counter_r;
    logic [$clog2(T2):0] output_counter_n, output_counter_r;
    
    // declare variables for debugging more easily;
    logic handshake_in, handshake_out;
    assign handshake_in = valid_i && ready_o;
    assign handshake_out = valid_o && yumi_i;
    
    // next address counter assignment
    assign input_counter_n = (valid_i && ready_o) && (input_counter_r != T1) ? 
        input_counter_r + 1 : input_counter_r;
    assign output_counter_n = valid_o && yumi_i && (output_counter_r != T2) ? 
        output_counter_r + 1 : output_counter_r;
    
    // Create an LFSR to assign other two ready and valid signals
    // this makes things more robust, since ready/valid should be independent of each other
    logic [3:0] lfsr_n, lfsr_r;
    assign lfsr_n = {lfsr_r[0]^lfsr_r[3], lfsr_r[3:1]};
    assign yumi_i = lfsr_r[0] && (output_counter_r != T2);
    assign valid_i = lfsr_r[2] && (input_counter_r != T1);
    
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
	`ifdef VIVADO
        fd = $fopen("output.csv", "w");
	`else
	    fd = $fopen("./python_scripts/output.csv", "w");
	`endif
        $fwrite(fd, "test_index,expected,received\n");
        forever begin
            @(negedge clk_i); // wait for the negative edge of the clock
            
            // reasoning: if the output counter has gone all the way up, we are done
            // sending data and can do final checks
            // should be able to check that valid_o is low
            if (output_counter_r == T2) begin
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
