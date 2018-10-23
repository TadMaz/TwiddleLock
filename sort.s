/******************************************************************************
* @file array.s
* @brief simple array declaration and iteration example
*
* Simple example of declaring a fixed-width array and traversing over the
* elements for printing.
*

******************************************************************************/
 
.global main
.func main
   
main:
    MOV R0, #0              @ initialze index variable
    LDR R1, =a

writeloop:
    LSL R2, R0, #2          @ multiply index*4 to get array offset
    ADD R2, R1, R2          @ R2 now has the element address
    MOV R6, #10            @ load 10 to r6
    SUB R6, R6, R0
    STR R6, [R2]              @ write the address of a[i] to a[i]
    ADD R0, R0, #1
    LSL R2, R0, #2          @ increment index
    ADD R2, R1, R2
    MOV R6, #2
    STR R6, [R2]
    ADD R0, R0, #1
    LSL R2, R0, #2
    ADD R2, R2, R1
    MOV R6, #8
    STR R6, [R2]
 
writedone:
    MOV R0, #0              @ initialze index variable
    MOV R2, #0
    MOV R3, #0
    MOV R6, #0

outerloop:
  CMP R0, #3
  BEQ sortdone
  LSL R2, R0, #2
  ADD R2, R2, R1
  MOV R6, R2
  ADD R3, R0, #1
  LDR R9, [R2]

innerloop:
    CMP R3, #3
    BEQ SWAP
    LSL R5, R3, #2
    ADD R5, R1, R5
    LDR R10, [R5]
    LDR R9, [R2]
    CMP R9, R10
    BLT CONT
    MOV R2, R5
    CONT:
       ADD R3, R3, #1
       B innerloop

SWAP:
  LDR R7, [R6]
  LDR R8, [R2]
  STR R7, [R2]
  STR R8, [R6]
  ADD R0, R0, #1
  B outerloop
  
sortdone:
  MOV R0, #0
  MOV R1, #0
  MOV R2, #0

/* FORKED FROM https://github.com/cmcmurrough/cse2312/blob/master/examples/array.s */
/* THIS IS JUST TO SHOW THAT IT SORTS*/
readloop:
    CMP R0, #3            @ check to see if we are done iterating3
    BEQ readdone            @ exit loop if done
    LDR R1, =a              @ get address of a
    LSL R2, R0, #2          @ multiply index*4 to get array offset
    ADD R2, R1, R2          @ R2 now has the element address
    LDR R1, [R2]            @ read the array at address
    PUSH {R0}               @ backup register before printf
    PUSH {R1}               @ backup register before printf
    PUSH {R2}               @ backup register before printf
    MOV R2, R1              @ move array value to R2 for printf
    MOV R1, R0              @ move array index to R1 for printf
    BL  _printf             @ branch to print procedure with return
    POP {R2}                @ restore register
    POP {R1}                @ restore register
    POP {R0}                @ restore register
    ADD R0, R0, #1          @ increment index
    B   readloop            @ branch to next loop iteration
readdone:
    B _exit                 @ exit if done

_exit:
    MOV R7, #4              @ write syscall, 4
    MOV R0, #1              @ output stream to monitor, 1
    MOV R2, #21             @ print string length
    LDR R1, =exit_str       @ string at label exit_str:
    SWI 0                   @ execute syscall
    MOV R7, #1              @ terminate syscall, 1
    SWI 0                   @ execute syscall
 
_printf:
    PUSH {LR}               @ store the return address
    LDR R0, =printf_str     @ R0 contains formatted string address
    BL printf               @ call printf
    POP {PC}                @ restore the stack pointer and return

/* FINISHED FORKING */
.data

.balign 4
a:              .skip       12
printf_str:     .asciz      "a[%d] = %d\n"
exit_str:       .ascii      "Terminating program.\n"
