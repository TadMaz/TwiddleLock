/* SELECTION SORT  */

.text
.global main
main:
@@@@@@@@@@@@@@@@@ INITIALIZE
    ldr r7, =return @ get ready to save
    str lr, [r7] @ link register for return
    mov r6, #0 @ keep count in r6
    ldr r4, =array @ keep constant &array in r4

@@@@@@@@@@@@@@@@@ INPUT
input:
    ldr r0, =prompt
    bl puts
    ldr r0, =scanFMT @ r0 <- &scan format
    ldr r1, =number @ r1 <- &number
    bl scanf @ call to scanf
    ldr r1, =number
    ldr r1, [r1]
    cmp r1, #0 @ look for sentinal (negative)
    blt isort @ goto isort function
    add r0, r4, r6, LSL #2 @ r0 <- &array[4*count]
    str r1, [r0] @ array[4*count] <- number
    add r6, r6, #1 @ count = count + 1
b input

@@@@@@@@@@@@@@@@@ ISORT
/*
@@ sort the integers
@ C/C++/Java Code:
@ null insertion(int[] a, int n)
@ { for (int i = 1; i < n; i++)
@ { temp = a[i];
@ j = i-1;
@ while (j >= 0 && temp < a[j])
@ { a[j+1] = a[j];
@ j = j-1;
@ }
@ a[j+1] = temp;
@ }
@ }
@@
*/
isort:
    mov r0, r4 @ r0 <- &array (a)
    mov r1, r6 @ r1 <- count = length (n)
    @
    mov r2, #1 @ i = 1
iloop: @ for-loop as while loop
    cmp r2, r1 @ i - n
    bge iloopend @ i >= n => loopend
    65
    10. Searching and Sorting
    add r10, r0, r2, LSL #2 @ temp = &array[4*i]
    ldr r10, [r10] @ temp = array[4*i]
    sub r3, r2, #1 @ j = i - 1
jloop: @ while-loop
    cmp r3, #0 @ j >= 0 ?
    blt jloopend
    add r9, r0, r3, LSL #2 @ r9 <- &array[4*j]
    ldr r9, [r9] @ r9 <- array[4*j]
    cmp r10, r9 @ temp < array[4*j] ?
    bge jloopend
    add r8, r0, r3, LSL #2
    add r8, r8, #4 @ r8 <- &array[4*(j+1)]
    str r9, [r8] @ a[j+1] <- a[j]
    sub r3, r3, #1 @ j <- j - 1
    b jloop
    @ end jloop
jloopend:
    add r3, r3, #1 @ j <- j+1
    add r8, r0, r3, LSL #2 @ r8 <- &array[4*(j+1)]
    str r10, [r8] @ a[j+1] <- temp
    add r2, r2, #1 @ i++
    b iloop
@ end iloop
iloopend:
    @ end isort
@@@@@@@@@@@@@@@@ OUTPUT
output:
    ldr r0, =result
    bl puts
    mov r5, #0 @ r5 counter
ploop: cmp r6, r5 @ n - counter
    ble exit @ done printing
    add r3, r4, r5, LSL #2 @ r3 <- &array[4*counter]
    ldr r1, [r3] @ r1 <- array[4*counter]
    ldr r0, =printFMT @ r0 <- &print format
    bl printf
    add r5, r5, #1 @ n++
    b ploop
@@@@@@@@@@@@@@@@ EXIT
exit:
    mov r0, r6 @ r0 = r6 return code = n
    ldr r1, =return @ r1 <- &return
    ldr lr, [r1] @ lr <- *r1 saved return address
    bx lr

@@@@@@@@@@@@@@@@@
.data
number: .word 0 @ place to hold input number
array: .space 100 @ room for 25 integers = 100 bytes
return: .word 0 @ place for return address of main
prompt: .asciz "Input a positive integer (negative to quit): "
result: .asciz "Sorted, those integers are: \n"
scanFMT: .asciz "%d"
printFMT: .asciz " %d\n"

@@@@@@@@@@@@@@@@@
/* External */
.global printf
.global scanf
.global puts
