# make          <- runs dve

all:	dve

##### 
# Modify starting here
#####

TB_NAME = cordic_mac_array_tb.sv
TESTBENCH = $(shell find . -name $(TB_NAME))
DESIGN_DIR = $(shell find ./hdl_design/hdl_design.srcs/design_sources -name "*.sv" -o -name "*.v")
VCS = SW_VCS=2023.12-SP2-1 vcs -sverilog +vc -Mupdate -line -full64 +define+SYNOPSIS

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
