# Makefile
all: first
first: first.o
	gcc -o $@ $+
first.o : first.s
	as -g -mfpu=vfpv2 -o $@ $<
clean:
	rm -vf fir *.o