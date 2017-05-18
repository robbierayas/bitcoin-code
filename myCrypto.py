import math
import hashlib
import utils

ordermap={
	0:7,
	1:4,
	2:13,
	3:1,
	4:10,
	5:6,
	6:15,
	7:3,
	8:12,
	9:0,
	10:9,
	11:5,
	12:2,
	13:14,
	14:11,
	15:8
}
functionmap_left={
	0:1,
	1:2,
	2:3,
	3:4,
	4:5
}
functionmap_right={
        0:5,
        1:4,
        2:3,
        3:2,
        4:1
}
constantmap_left={
        0:'00000000',
        1:'5A827999',
        2:'6ED9EBA1',
        3:'8F1BBCDC',
        4:'A953FD4E'
}
constantmap_right={
        0:'50A28BE6',
        1:'5C4DD124',
        2:'6D703EF3',
        3:'7A6D76E9',
        4:'00000000'
}

#md160 paper version

#shiftmap_left={
#0:11, 1:14, 2:15, 3:12, 4:5, 5:8, 6:7, 7:9, 8:11, 9:13, 10:14, 11:15, 12:6, 13:7, 14:9, 15:8,
#16:12, 17:13, 18:11, 19:15, 20:6, 21:9, 22:9, 23:7, 24:12, 25:15, 26:11, 27:13, 28:7, 29:8, 30:7, 31:7,
#32:13, 33:15, 34:14, 35:11, 36:7, 37:7, 38:6, 39:8, 40:13, 41:14, 42:13, 43:12, 44:5, 45:5, 46:6, 47:9,
#48:14, 49:11, 50:12, 51:14, 52:8, 53:6, 54:5, 55:5, 56:15, 57:12, 58:15, 59:14, 60:9, 61:9, 62:8, 63:6,
#64:15, 65:12, 66:13, 67:13, 68:9, 69:5, 70:8, 71:6, 72:14, 73:11, 74:12, 75:11, 76:8, 77:6, 78:5, 79:5
#}
#shiftmap_right=shiftmap_left



#article 13 version
shiftmap_left={
0:11, 1:14, 2:15, 3:12, 4:5, 5:8, 6:7, 7:9, 8:11, 9:13, 10:14, 11:15, 12:6, 13:7, 14:9, 15:8,
16:7, 17:6, 18:8, 19:13, 20:11, 21:9, 22:7, 23:15, 24:7, 25:12, 26:15, 27:9, 28:11, 29:7, 30:13, 31:12,
32:11, 33:13, 34:6, 35:7, 36:14, 37:9, 38:13, 39:15, 40:14, 41:8, 42:13, 43:6, 44:5, 45:12, 46:7, 47:5,
48:11, 49:12, 50:14, 51:15, 52:14, 53:15, 54:9, 55:8, 56:9, 57:14, 58:5, 59:6, 60:8, 61:6, 62:5, 63:12,
64:9, 65:15, 66:5, 67:11, 68:6, 69:8, 70:13, 71:12, 72:5, 73:12, 74:13, 75:14, 76:11, 77:8, 78:5, 79:6
}
shiftmap_right={
0:8, 1:9, 2:9, 3:11, 4:13, 5:15, 6:15, 7:5, 8:7, 9:7, 10:8, 11:11, 12:14, 13:14, 14:12, 15:6,
16:9, 17:13, 18:15, 19:7, 20:12, 21:8, 22:9, 23:11, 24:7, 25:7, 26:12, 27:7, 28:6, 29:15, 30:13, 31:11,
32:9, 33:7, 34:15, 35:11, 36:8, 37:6, 38:6, 39:14, 40:12, 41:13, 42:5, 43:14, 44:13, 45:13, 46:7, 47:5,
48:15, 49:5, 50:8, 51:11, 52:14, 53:14, 54:6, 55:14, 56:6, 57:9, 58:12, 59:9, 60:12, 61:5, 62:15, 63:8,
64:8, 65:5, 66:12, 67:9, 68:12, 69:5, 70:14, 71:6, 72:8, 73:13, 74:6, 75:5, 76:15, 77:13, 78:11, 79:11
}
rho={
	0:7,1:4,2:13,3:1,4:10,5:6,6:15,7:3,8:12,9:0,10:9,11:5,12:2,13:14,14:11,15:8
}

wordselect_left={
0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 12:12, 13:13, 14:14, 15:15,
16:7, 17:4, 18:13, 19:1, 20:10, 21:6, 22:15, 23:3, 24:12, 25:0, 26:9, 27:5, 28:2, 29:14, 30:11, 31:8,
32:3, 33:10, 34:14, 35:4, 36:9, 37:15, 38:8, 39:1, 40:2, 41:7, 42:0, 43:6, 44:13, 45:11, 46:5, 47:12,
48:1, 49:9, 50:11, 51:10, 52:0, 53:8, 54:12, 55:4, 56:13, 57:3, 58:7, 59:15, 60:14, 61:5, 62:6, 63:2,
64:4, 65:0, 66:5, 67:9, 68:7, 69:12, 70:2, 71:10, 72:14, 73:1, 74:3, 75:8, 76:11, 77:6, 78:15, 79:13
}
wordselect_right={
0:5, 1:14, 2:7, 3:0, 4:9, 5:2, 6:11, 7:4, 8:13, 9:6, 10:15, 11:8, 12:1, 13:10, 14:3, 15:12,
16:6, 17:11, 18:3, 19:7, 20:0, 21:13, 22:5, 23:10, 24:14, 25:15, 26:8, 27:12, 28:4, 29:9, 30:1, 31:2,
32:15, 33:5, 34:1, 35:3, 36:7, 37:14, 38:6, 39:9, 40:11, 41:8, 42:12, 43:2, 44:10, 45:0, 46:4, 47:13,
48:8, 49:6, 50:4, 51:1, 52:3, 53:11, 54:15, 55:0, 56:5, 57:12, 58:2, 59:13, 60:9, 61:7, 62:10, 63:14,
64:12, 65:15, 66:10, 67:4, 68:1, 69:5, 70:8, 71:7, 72:6, 73:2, 74:13, 75:14, 76:0, 77:3, 78:9, 79:11
}



#overflow mask 2^32
mask=4294967296
roundnum=0
def myRipeMD160(public_key):
        message=hashlib.sha256(public_key.decode('hex')).hexdigest()
	bmessage=bin(int(message,16))[2:]
	#append one and zeros 
	length=len(bmessage)
	bmessage=bmessage.ljust(length+1,'1').ljust(448,'0')
        #append a 64 bit length value to message
        blength=bin(length)[2:].zfill(64)
	blength_little_end=''
	for x in range(len(blength)/32):
        	blength_little_end += little_end(blength[32*x:32*(x+1)],2)
	bmessage+=blength_little_end[32:]+blength_little_end[:32]
	hmessage=hex(int(bmessage,2))[2:-1]
	#split message to 16 32-bit words for X[]
	X=[little_end(hmessage[i:i+8]) for i in range(0, len(hmessage)-1, 8)]
	print 'X {}'.format(X)
	#initialise 5 word 160 bit buffer (ABCDE) to ()
	Ai=int('67452301',16)
	Bi=int('efcdab89',16)
	Ci=int('98badcfe',16)
	Di=int('10325476',16)
	Ei=int('c3d2e1f0',16)
	A=Ai
        B=Bi
	C=Ci
        D=Di
	E=Ei
	Ar=A
	Br=B
	Cr=C
	Dr=D
	Er=E
	print 'h_initial {} {} {} {} {}'.format(hex(A),hex(B),hex(C),hex(D),hex(E))
	#process message in 16_word (512 bit) chunks
	##use 10 rounds of 16 bit ops on message block and buffer - in 2 parallel lines of 5
	for round in range(0,5):
		roundnum=round
		#print 'roundnum {}'.format(roundnum)
		for j in range(0,16):
			#X
			rho_j=rho.get(j,"nothing")
			pi_j=(9*j+5)%16

			#r=(rho_j^round)%16
			#if round==0:
			#	r=j
			#rr=(pi_j*rho_j^round)%16
			r=wordselect_left.get(round*16+j,"nothing")
			rr=wordselect_right.get(round*16+j,"nothing")

			Xl=int(X[r],16)
			Xr=int(X[rr],16)

			#K
			K=int(constantmap_left.get(round, "nothing"),16)
	                Kr=int(constantmap_right.get(round, "nothing"),16)
	
			#s
			s=shiftmap_left.get(round*16+j,"nothing")
                        sr=shiftmap_right.get(round*16+j,"nothing")
			
			#left
			#print 'left'
			A,B,C,D,E=compression(A,B,C,D,E,functionmap_left.get(round, "nothing"),Xl,K,s)
			#print ''
                        #right
			#print 'right'
                        Ar,Br,Cr,Dr,Er=compression(Ar,Br,Cr,Dr,Er,functionmap_right.get(round, "nothing"),Xr,Kr,sr)
			if (round==4)&(j>=11):
				print 'round {} j {}, K {}, s {}, r {} rr {} Xl {}'.format(round,j,K,s,r,rr,Xl)
				print 'h_left {} {} {} {} {}'.format(hex(A),hex(B),hex(C),hex(D),hex(E))
				print 'h_right {} {} {} {} {}'.format(hex(Ar),hex(Br),hex(Cr),hex(Dr),hex(Er))
				print ''

	##add output to message to form new buffer value
	#convert h0, h1, h2, h3 and h4 in hex, then add, little endian
	Af=(Bi+C+Dr)%mask
	Bf=(Ci+D+Er)%mask
	Cf=(Di+E+Ar)%mask
	Df=(Ei+A+Br)%mask
	Ef=(Ai+B+Cr)%mask
	Af_hex=hex(Af)[2:].zfill(8)
	Bf_hex=hex(Bf)[2:].zfill(8)
	Cf_hex=hex(Cf)[2:].zfill(8)
	Df_hex=hex(Df)[2:].zfill(8)
	Ef_hex=hex(Ef)[2:].zfill(8)
	print 'hnew {} {} {} {} {}'.format(little_end(Af_hex),little_end(Bf_hex),little_end(Cf_hex),little_end(Df_hex),little_end(Ef_hex))
	hex_data=(little_end(Af_hex))+(little_end(Bf_hex))+(little_end(Cf_hex))+(little_end(Df_hex))+little_end(Ef_hex)
	print 'hex_data {}'.format(hex_data)
	hex_string=hex(int(hex_data, 16))[2:-1]

	print 'hex_string {}'.format(hex_string)
	hex_string=hex_string.decode('hex')
	#output hash value is the final buffer value
	return hex_string

def compression(A,B,C,D,E,f,X,K,s):
	#print 'compression {}'.format(A)
	A_out,C_out=operation(A,B,C,D,E,f,X,K,s)
        A=E%mask
        C=B%mask
        E=D%mask
        B=A_out
        D=C_out
	return A,B,C,D,E

def operation(A,B,C,D,E,f,X,K,s):
	A_out=A
	if f==1:
		A_out=(A_out+function1(B,C,D))%mask
	elif f==2:
                A_out=(A_out+function2(B,C,D))%mask
        elif f==3:
                A_out=(A_out+function3(B,C,D))%mask
        elif f==4:
                A_out=(A_out+function4(B,C,D))%mask
        elif f==5:
                A_out=(A_out+function5(B,C,D))%mask
	A_out000=(A_out+X)%mask
	A_out00=(A_out000+K)%mask
	A_out0=cyclicShift(A_out00,s)%mask
	A_out1=(A_out0+E)%mask
	#if K==2840853838:
		#print 'f {} {} {} {} {}'.format(f,B,C,D,hex(function5(B,C,D)%mask))
		#print 'A {}'.format(hex(A))
		#print 'A_out4 {}'.format(hex((A+function5(B,C,D))%mask))
		#print 'A_out3 {}'.format(hex(A_out000))
		#print 'A_out2 {}'.format(hex(A_out00))
		#print 'A_out1 {}'.format(hex(A_out0))
		#print 'A_out {}'.format(hex(A_out1))

	C_out=cyclicShift(C,10)%mask
	return A_out1%mask,C_out%mask

def ordering(i):
	return ordermap.get(i, "nothing")

def function1(B,C,D):
	binB=int(bin(B)[2:],2)
	
        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)

        num=binB^binC^binD
	return num

def function2(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binC)|(~binB&binD)
        return num

def function3(B,C,D):
        binB=int(bin(B)[2:],2)
        binC=int(bin(C)[2:],2)
        binD=int(bin(D)[2:],2)
        num=(binB|~binC)^binD
        return num


def function4(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binD)|(binC&~binD)
        return num


def function5(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
	num=binB^(binC|~binD)
        return num

def cyclicShift(C,s):
	C_rot=(C << s) | (C >> 32-s)
	return C_rot

def little_end(string,base = 16):
    t = ''
    if base == 2:
        s= 8
    if base == 16:
        s = 2
    for x in range(len(string)/s):
        t = string[s*x:s*(x+1)] + t
    return t