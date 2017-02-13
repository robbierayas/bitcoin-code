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

shiftmap_left={
0:11, 1:14, 2:15, 3:12, 4:5, 5:8, 6:7, 7:9, 8:11, 9:13, 10:14, 11:15, 12:6, 13:7, 14:9, 15:8,
16:12, 17:13, 18:11, 19:15, 20:6, 21:9, 22:9, 23:7, 24:12, 25:15, 26:11, 27:13, 28:7, 29:8, 30:7, 31:7,
32:13, 33:15, 34:14, 35:11, 36:7, 37:7, 38:6, 39:8, 40:13, 41:14, 42:13, 43:12, 44:5, 45:5, 46:6, 47:9,
48:14, 49:11, 50:12, 51:14, 52:8, 53:6, 54:5, 55:5, 56:15, 57:12, 58:15, 59:14, 60:9, 61:9, 62:8, 63:6,
64:15, 65:12, 66:13, 67:13, 68:9, 69:5, 70:8, 71:6, 72:14, 73:11, 74:12, 75:11, 76:8, 77:6, 78:5, 79:5
}
shiftmap_right=shiftmap_left



#article 13 version
#shiftmap_left={
#0:11, 1:14, 2:15, 3:12, 4:5, 5:8, 6:7, 7:9, 8:11, 9:13, 10:14, 11:15, 12:6, 13:7, 14:9, 15:8,
#16:7, 17:6, 18:8, 19:13, 20:11, 21:9, 22:7, 23:15, 24:7, 25:12, 26:15, 27:9, 28:11, 29:7, 30:13, 31:12,
#32:11, 33:13, 34:6, 35:7, 36:14, 37:9, 38:13, 39:15, 40:14, 41:8, 42:13, 43:6, 44:5, 45:12, 46:7, 47:5,
#48:11, 49:12, 50:14, 51:15, 52:14, 53:15, 54:9, 55:8, 56:9, 57:14, 58:5, 59:6, 60:8, 61:6, 62:5, 63:12,
#64:9, 65:15, 66:5, 67:11, 68:6, 69:8, 70:13, 71:12, 72:5, 73:12, 74:13, 75:14, 76:11, 77:8, 78:5, 79:6
#}
#shiftmap_right={
#0:8, 1:9, 2:9, 3:11, 4:13, 5:15, 6:15, 7:5, 8:7, 9:7, 10:8, 11:11, 12:14, 13:14, 14:12, 15:6,
#16:9, 17:13, 18:15, 19:7, 20:12, 21:8, 22:9, 23:11, 24:7, 25:7, 26:12, 27:7, 28:6, 29:15, 30:13, 31:11,
#32:9, 33:7, 34:15, 35:11, 36:8, 37:6, 38:6, 39:14, 40:12, 41:13, 42:5, 43:14, 44:13, 45:13, 46:7, 47:5,
#48:15, 49:5, 50:8, 51:11, 52:14, 53:14, 54:6, 55:14, 56:6, 57:9, 58:12, 59:9, 60:12, 61:5, 62:15, 63:8,
#64:8, 65:5, 66:12, 67:9, 68:12, 69:5, 70:14, 71:6, 72:8, 73:13, 74:6, 75:5, 76:15, 77:13, 78:11, 79:11
#}
rho={
	0:7,1:4,2:13,3:1,4:10,5:6,6:15,7:3,8:12,9:0,10:9,11:5,12:2,13:14,14:11,15:8
}


def myRipeMD160(test_input):
	rinput=hashlib.sha256(test_input.decode('hex')).digest()

	length=int(len(rinput)*math.log(16,2))
	print 'bit size {}'.format(length)
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(rinput)
	ripe=utils.base58CheckEncode(0, ripemd160.digest())

	
        input=hashlib.sha256(test_input.decode('hex')).hexdigest()


	#pad messages so its length is 448 mod 512
	numberOfZeros=int(511-((length+64)%512))
	print 'zeros {}'.format(numberOfZeros)
        print 'input {}'.format(input)
	#print "hex? {}".format(int(input,16))
	binput=bin(int(input,16))[2:]
	print binput
	print type(binput)

        #append a 64 bit length value to message
        blength=bin(length)[2:].zfill(64)
	binput=binput.ljust(length+1,'1').ljust(448,'0')+blength
	print 'bit size {}'.format(len(binput))
	print 'message length {}'.format(binput)
	hinput=hex(int(binput,2))[2:-1]
        print 'message length {}'.format(hinput)

	#binput_check=bin(int(hinput,16))[2:]
        #print 'binput_check {}'.format(binput_check)
        #print type(binput_check)

	
	

	#split message to 16 32-bit blocks for X[]
	X=[hinput[i:i+8] for i in range(0, len(hinput)-1, 8)]
	print 'split message {}'.format(X)


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

	#process message in 16_word (512 bit) chunks
	##use 10 rounds of 16 bit ops on message block and buffer - in 2 parallel lines of 5
	for round in range(0,5):
		for j in range(0,16):
			#X
			rho_j=rho.get(j,"nothing")
			pi_j=(9*j+5)%16

			r=(rho_j^round)%16
			if round==0:
				r=j
			rr=(pi_j*rho_j^round)%16

#??????????????#
			Xl=int(X[r],16)
			Xr=int(X[rr],16)
#??????????????#
			#K
			K=int(constantmap_left.get(round, "nothing"),16)
	                Kr=int(constantmap_right.get(round, "nothing"),16)
	
			#s
			s=shiftmap_left.get(round*15+j,"nothing")
                        sr=shiftmap_right.get(round*15+j,"nothing")


			#left
			A,B,C,D,E=compression(A,B,C,D,E,functionmap_left.get(round, "nothing"),Xl,K,s)

                       #right
                        Ar,Br,Cr,Dr,Er=compression(Ar,Br,Cr,Dr,Er,functionmap_right.get(round, "nothing"),Xr,K,s)
#		next?


	##add output to input to form new buffer value
	#convert h0, h1, h2, h3 and h4 in hex, then add, low order first???
	Af=Bi+C+Dr
	Bf=Ci+D+Er
	Cf=Di+E+Ar
	Df=Ei+A+Br
	Ef=Ai+B+Cr
	print 'Af {}'.format(Af)

	answer=0
	hex_data1 = Af+Bf+Cf+Df+Ef;
	answer=answer+hex_data1
	print 'ripe1 {}'.format(ripe)
	print 'ripe2 {}'.format(answer)
	#output hash value is the final buffer value
	ripe2=answer
        hashLength=len(ripe2)*math.log(16,2)
        print 'bit size {}'.format(hashLength)





	return ripe

def compression(A,B,C,D,E,f,X,K,s):
	A_out,C_out=operation(A,B,C,D,E,f,X,K,s)
        A=E
        B=A_out
        C=B
        D=C_out
        E=D
	return A,B,C,D,E

def operation(A,B,C,D,E,f,X,K,s):
	A_out=A
	if f==1:
		A_out=A_out+function1(B,C,D)
	elif f==2:
                A_out=A_out+function2(B,C,D)
        elif f==3:
                A_out=A_out+function3(B,C,D)
        elif f==4:
                A_out=A_out+function4(B,C,D)
        elif f==5:
                A_out=A_out+function5(B,C,D)
	A_out=A_out+X
	A_out=A_out+K
	A_out=cyclicShift(A_out,s)
	A_out=A_out+E
	C_out=cyclicShift(C,10)
	return A_out,C_out

def ordering(i):
	return ordermap.get(i, "nothing")

def function1(B,C,D):
#	print 'function 1'
	binB=int(bin(B)[2:],2)
	
        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
#	print 'binB {}'.format(binB)
#        print 'binC {}'.format(binC)
#        print 'binD {}'.format(binD)

        num=binB^binC^binD
	#print 'B {}'.format(int(bin(B)))
        #print 'C {}'.format(bin(C))
        #print 'D {}'.format(bin(D))
	#num=bin(bin(B)^bin(C)^bin(D))
	print num
	return num

def function2(B,C,D):

#        print 'function 2'
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binC)|(~binB&binD)

#        num=bin((bin(B)&bin(C))|(~bin(B)&bin(D)))
        return num

def function3(B,C,D):
#        print 'function 3'
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB|~binC)^binD

#        num=bin((bin(B)|~bin(C))^bin(D))
        return num


def function4(B,C,D):
#        print 'function 4'
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binD)|(binC&~binD)

#        num=bin((bin(B)&bin(D))|(bin(C)&~bin(D)))
        return num


def function5(B,C,D):
#        print 'function 5'
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
	num=binB^binC|~binD

#       num=bin(bin(B)^(bin(C)|~bin(D)))
        return num

def cyclicShift(C,s):
	C_rot=C
	return C_rot
