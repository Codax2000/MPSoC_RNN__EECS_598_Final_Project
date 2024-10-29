# make          <- runs simv (after compiling simv if needed)
# make simv     <- compiles simv without running
# make dve      <- runs GUI debugger (after compiling it if needed)
# make syn      <- runs syn_simv (after synthesizing if needed then 
#                                 compiling syn_simv if needed)
# make clean    <- remove files created during compilations (but not synthesis)
# make nuke     <- remove all files created during compilation and synthesis
#
# To compile additional files, add them to the TESTBENCH or SIMFILES as needed
# Every .vg file will need its own rule and one or more synthesis scripts
# The information contained here (in the rules for those vg files) will be 
# similar to the information in those scripts but that seems hard to avoid.
#

all:	dve

##### 
# Modify starting here
#####

TESTBENCH = hdl_design/hdl_design.srcs/template_tb/sv/template_tb.sv
DESIGN_DIR = $(shell find ./hdl_design/hdl_design.srcs/design_sources -name "*.sv" -o -name "*.v")
VCS = SW_VCS=2020.12-SP2-1 vcs -sverilog +vc -Mupdate -line -full64 +define+SYNOPSIS

#####
# Should be no need to modify after here
#####
.PHONY: dve clean nuke

dve:	 
	$(VCS) $(DESIGN_DIR) $(TESTBENCH) -o dve -R -gui -debug_acccess+all -kdb | tee dve.log



clean:
	rm -rvf simv *.daidir csrc vcs.key program.out \
	syn_simv syn_simv.daidir syn_program.out \
	dve *.vpd *.vcd *.dump ucli.key \
        inter.fsdb novas* verdiLog	

nuke:	clean
	rm -rvf *.vg *.rep *.db *.chk *.log *.out *.ddc *.svf DVEfiles/
