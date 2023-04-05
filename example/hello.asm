        ORG  0500H

        CPU 1802

R0        EQU 0
R1        EQU 1
R2        EQU 2
R3        EQU 3
R4        EQU 4
R5        EQU 5
R6        EQU 6
R7        EQU 7
R8        EQU 8
R9        EQU 9
RA        EQU 10
RB        EQU 11
RC        EQU 12
RD        EQU 13
RE        EQU 14
RF        EQU 15

        LDI  81H
        PHI  R1
        LDI  31H
        PLO  R1                  ; R1 = 0x8131, clear screen routine
        LDI  83H
        PHI  R3
        LDI  0B9H
        PLO  R3                  ; R3 = 0x83B9, M(R3) = 0
        LDI  08H
        PHI  R4
        GLO  RC
        PLO  R4                  ; R4 = 0x800, pointer to VRAM
        LDI  83H
        PHI  R5
        LDI  0B9H
        PLO  R5                  ; R5 = 0x83B9, M(R5) = 0
        LDI  40H
        PHI  R9
        LDI  20H
        PLO  R9
        SEP  R1                  ; CALL clear screen

        LDI  81H
        PHI  R1
        LDI  55H
        PLO  R1                  ; R1 = 0x8155, screen output routine
        LDI  83H
        PHI  R5
        LDI  0BBH
        PLO  R5                  ; R5 = 0x83BB, M(R5) = 0x80, 
        LDI  08H
        PHI  R4
        LDI  00H
        PLO  R4                  ; R4 = 0x0800, pointer to VRAM

        LDI  05H
        PHI  R6
        LDI  50H
        PLO  R6                  ; R6 = 0x0550, "HELLO"
        SEP  R1

        LDI  0BCH
        PLO  R5                  ; R5 = 0x83BC, M(R5) = 0xC0, red
        LDI  09H
        PHI  R4
        LDI  00H
        PLO  R4                  ; R4 = 0x0800, pointer to VRAM
        SEP  R1

        SEQ
        LDI  03H
        PHI  RC
        LDI  81H
        PHI  R1
        LDI  0ABH
        PLO  R1
        SEP  R1
        REQ 
LOOP
        BR   LOOP

        ORG  0550H

        DB 22H, 1CH, 2AH, 2AH, 30H, 88H
        DB 18H, 44H, 16H, 1CH, 36H, 3EH, 24H, 38H, 24H, 30H, 2EH, 88H
