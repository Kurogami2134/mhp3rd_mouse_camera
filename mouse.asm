.psp

yaw_hook equ 0x88E4F18
pitch_hook equ 0x88E5F80
main equ 0x8800500
fixu equ 0x88E5568
fixd equ 0x88E5494

.createfile "main.bin", main
yawmain:
	lui			at, yaw / 0x10000
	lwc1		f2, yaw & 0xFFFF(at)
	j			yaw_hook + 8
	nop
	
yaw:
	.word		0x3f800000  ; 1 degree by default
pitch:
	.word		0x00000000
pitchmain:
	lui			at, pitch / 0x10000
	lw			v0, pitch & 0xFFFF(at)
	j			pitch_hook + 8
	nop
.close

.createfile "yaw_hook.bin", yaw_hook
yaw_h:
	j			yawmain
.close

.createfile "pitch_hook.bin", pitch_hook
pitch_h:
	j			pitchmain
	nop
	nop
.close

.createfile "fixu.bin", fixu
fixup:
	nop
.close

.createfile "fixd.bin", fixd
fixdown:
	nop
.close