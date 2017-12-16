import math
import hashlib
import utils
import binascii

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


#target 5 word 160 bit buffer (ABCDE) to ()
A0=int('67452301',16)
B0=int('efcdab89',16)
C0=int('98badcfe',16)
D0=int('10325476',16)
E0=int('c3d2e1f0',16)


#overflow mask 2^32
mask=4294967296;

def myRollBack(address):
	print 'Rollback address {}'.format(address)
	basedecode=utils.base58CheckDecode(address)
	print 'Rollback basedecode {}'.format(basedecode)
	hex_data=basedecode.encode('hex')
	print 'Rollback hexl {}'.format(hex_data)
	Af_hex=hex_data[:8]
	Bf_hex=hex_data[8:16]
	Cf_hex=hex_data[16:24]
	Df_hex=hex_data[24:32]
	Ef_hex=hex_data[32:40]
	print 'hnew {} {} {} {} {}'.format(Af_hex,Bf_hex,Cf_hex,Df_hex,Ef_hex)
	print 'TO DO un-add final values'
	Al=int('82a24ea5',16)
	Bl=int('11e8ef41',16)
	Cl=int('e109aea8',16)
	Dl=int('e3474402',16)
	El=int('302cc6dc',16)

	Ar=int('5592219f',16)
	Br=int('4eb93ee3',16)
	Cr=int('a91d7fa6',16)
	Dr=int('0c8673c2',16)
	Er=int('ac4b8c30',16)
	print ''
	print 'h_left 15 {} {} {} {} {}'.format(hex(Al),hex(Bl),hex(Cl),hex(Dl),hex(El))
	print 'h_right 15 {} {} {} {} {}'.format(hex(Ar),hex(Br),hex(Cr),hex(Dr),hex(Er))
	print ''
	X=['' for i in range(8)]+[int('00000080',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000100',16), int('00000000',16)]
	#X[6]=int('9fd3a02e',16)
	Xrr=['' for i in range(8)]+[int('00000080',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000000',16), int('00000100',16), int('00000000',16)]
	for round in range(4,3,-1):
	#for round in range(4,-1,-1):
		print 'round {}'.format(round)
		for j in range(15,10,-1):
		#for j in range(15,-1,-1):
			print 'j {}'.format(j)
			



			#left
			#print 'left'
			#Al,Bl,Cl,Dl,El,Xl=dcompression(Al,Bl,Cl,Dl,El,functionmap_left.get(round, "nothing"),X[r],K,s)
			Al,Bl,Cl,Dl,El,Xl=rcompression(Al,Bl,Cl,Dl,El,functionmap_left.get(round, "nothing"),X,round,j)
			#print ''
                        #right
			#print 'right'
                        #Ar,Br,Cr,Dr,Er,Xr=dcompression(Ar,Br,Cr,Dr,Er,functionmap_right.get(round, "nothing"),Xrr[rr],Kr,sr)
			#Ar,Br,Cr,Dr,Er,Xr=rcompression(Ar,Br,Cr,Dr,Er,functionmap_right.get(round, "nothing"),X,round,j)
			print ''

			print 'h_left {} {} {} {} {} {}'.format(j-1,hex(Al),hex(Bl),hex(Cl),hex(Dl),hex(El))
			print 'X {} '.format(X)
			#print 'h_right {} {} {} {} {} {}'.format(j-1,hex(Ar),hex(Br),hex(Cr),hex(Dr),hex(Er))

def rcompression(A,B,C,D,E,f,X,round,j):
	#r
	r=wordselect_left.get(round*16+j,"nothing")
	#rr=wordselect_right.get(round*16+j,"nothing")
	#K
	K=int(constantmap_left.get(round, "nothing"),16)
	#Kr=int(constantmap_right.get(round, "nothing"),16)
	
	#s
	s=shiftmap_left.get(round*16+j,"nothing")
        #sr=shiftmap_right.get(round*16+j,"nothing")
	# print 'round {} j {}, K {}, s {}, r {}'.format(round,j,K,s,r)
	X_out=X[r]
	#terminate recursion
	if X[r]!='':
		# print 'X defined skip recursion'
		# print 'pre-doperation (j={}){} {} {} {} {} '.format(j,hex(A),hex(B),hex(C),hex(D),hex(E))
		A_out,C_out,X_out=doperation(A,B,C,D,E,f,X[r],K,s)
		if X[r]!=X_out:
			print 'Xr!=Xout {} {}'.format(X[r],X_out)
		# print 'post-doperation(j={}) {} {} {} {} {} '.format(j-1,hex(A),hex(B),hex(C),hex(D),hex(E))
	else:
		# print 'X undefined recurse'
		# print 'pre-findX_r {} {} {} {} {} '.format(hex(A),hex(B),hex(C),hex(D),hex(E))
		A_out,C_out,X_out=findX_r(A,B,C,D,E,f,X,r,K,s,round,j)
		# print 'post-findX_r {} {} {} {} {} '.format(hex(A_out),hex(B),hex(C_out),hex(D),hex(E))
		# print 'post-findX_r X {} '.format(X_out)
		#Save X value
		X[r]=X_out
	D=E
	B=C
	E=A
	A=A_out
	C=C_out
		
	#print 'compression {}'.format(B)

	return A,B,C,D,E,X_out

def findX_r(A,B,C,D,E,f,X,r,K,s,round,j):
	print '          findX_r'
	C_out=ROR(D,10)%mask
	#print '          f {}'.format(hex(f))
	A_out=B
	#print '          A_out {}'.format(hex(A_out))
	A_out1=(A_out-A)%mask
	#print '          A_out1 {}'.format(hex(A_out1))
	A_out2=ROR(A_out1,s)%mask
	#print '          A_out2 {}'.format(hex(A_out2))
	A_out3=(A_out2-K)%mask
	#print '          A_out3 {}'.format(hex(A_out3))

	print '         begin finding X'
	Cl=C_out
	Dl=E
	Bl=C
	El=A

	foundX=False
	i_A=3785517728
	while not foundX:
		# #estimate Al
		Al=i_A

		#find X
		# print '         PRE_RCOMPRESSION {} {} {} {} {} '.format(hex(Al),hex(Bl),hex(Cl),hex(Dl),hex(El))
		All,Bll,Cll,Dll,Ell,Xl2=rcompression(Al,Bl,Cl,Dl,El,f,X,round,j-1)
		# print '         post-rcompression All {} Bll {} Cll {} Dll {} Ell {} '.format(hex(All),hex(Bll),hex(Cll),hex(Dll),hex(Ell))
		# print '         post-rcompression round {} j-1 {} Xl {}'.format(round,j-1,Xl2)
		
		# check value
		print '         check value'
		Ac,Bc,Cc,Dc,Ec=compression(All,Bll,Cll,Dll,Ell,f,Xl2,round,j-1)
		# print '         recompress Ac {} Bc {} Cc {} Dc {} Ec {} '.format(hex(Ac),hex(Bc),hex(Cc),hex(Dc),hex(Ec))

		# # estimate Xl
		i_X=0
		while i_X<4294967296:
			Xl=i_X
			# check value
			# print '         Xl {}'.format(Xl)
			#
			Af,Bf,Cf,Df,Ef=compression(Ac,Bc,Cc,Dc,Ec,f,Xl,round,j)
			# Af=Ec%mask
			# Cf=Bc%mask
			# Ef=Dc%mask
			# Bf=Ac
			# Df=Cc
			# print '         recompress 2 Af {} Bf {} Cf {} Df {} Ef {} '.format(hex(Af),hex(Bf),hex(Cf),hex(Df),hex(Ef))

			if Bf==B:
				foundX=True
				X_out=Xl
				i_X=5000000000
				#use Xl
				A_out4=(A_out3-Xl)%mask
				print '         bruteforce worked'
			i_X=i_X+1

		i_A=i_A+1
		if i_A==3785517729:
			foundX=True
			print '         bruteforce done'
		
	
	# print 'A_out4 {}'.format(hex(A_out4))
	# print 'dfunction5 {} {} {} {}'.format(C,C_out,E,hex(dfunction5(C,C_out,E)%mask))
	if f==1:
		A_out4=(A_out4-dfunction1(C,C_out,E))%mask
	elif f==2:
                A_out4=(A_out4-dfunction2(C,C_out,E))%mask
        elif f==3:
                A_out4=(A_out4-dfunction3(C,C_out,E))%mask
        elif f==4:
                A_out4=(A_out4-dfunction4(C,C_out,E))%mask
        elif f==5:
                A_out4=(A_out4-dfunction5(C,C_out,E))%mask
	# print 'A_out4 {}'.format(hex(A_out4))
	return A_out4%mask,C_out%mask,X_out

def dcompression(A,B,C,D,E,f,X,K,s):
	#start
	A_out,C_out,X_out=doperation(A,B,C,D,E,f,X,K,s)
	D=E
	B=C
	E=A

	A=A_out
	C=C_out
	#print 'compression {}'.format(B)

	return A,B,C,D,E,X_out


def doperation(A,B,C,D,E,f,X,K,s):
	C_out=ROR(D,10)%mask
	# print '         doperation f {}'.format(hex(f))
	# print '         doperation s {} K {} X {}'.format(s,K,X)
	A_out=B
	# print '         doperation A_out {}'.format(hex(A_out))
	A_out1=(A_out-A)%mask
	# print 'A_out1 {}'.format(hex(A_out1))
	A_out2=ROR(A_out1,s)%mask
	# print 'A_out2 {}'.format(hex(A_out2))
	A_out3=(A_out2-K)%mask
	# print 'A_out3 {}'.format(hex(A_out3))
	A_out4=(A_out3-X)%mask
	# print '         doperation A_out4 {}'.format(hex(A_out4))
	#print 'dfunction5 {} {} {} {}'.format(C,C_out,E,hex(dfunction5(C,C_out,E)%mask))
	if f==1:
		A_out4=(A_out4-dfunction1(C,C_out,E))%mask
	elif f==2:
                A_out4=(A_out4-dfunction2(C,C_out,E))%mask
        elif f==3:
                A_out4=(A_out4-dfunction3(C,C_out,E))%mask
        elif f==4:
                A_out4=(A_out4-dfunction4(C,C_out,E))%mask
        elif f==5:
                A_out4=(A_out4-dfunction5(C,C_out,E))%mask
	# print '         doperation A_out4 {}'.format(hex(A_out4))
	return A_out4%mask,C_out%mask,X

def dfunction1(B,C,D):
	binB=int(bin(B)[2:],2)
	
        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)

        num=binB^binC^binD
	return num

def dfunction2(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binC)|(~binB&binD)
        return num

def dfunction3(B,C,D):
        binB=int(bin(B)[2:],2)
        binC=int(bin(C)[2:],2)
        binD=int(bin(D)[2:],2)
        num=(binB|~binC)^binD
        return num


def dfunction4(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
        num=(binB&binD)|(binC&~binD)
        return num


def dfunction5(B,C,D):
        binB=int(bin(B)[2:],2)

        binC=int(bin(C)[2:],2)

        binD=int(bin(D)[2:],2)
	num=binB^(binC|~binD)
        return num


def ROL(C,s):
	C_rot=(C << s) | (C >> 32-s)
	return C_rot

def ROR(C,s):
	C_rot=(C >> s) | (C << 32-s)
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








def compression(A,B,C,D,E,f,X,round,j):
	
	#r
	r=wordselect_left.get(round*16+j,"nothing")
	#rr=wordselect_right.get(round*16+j,"nothing")
	#K
	K=int(constantmap_left.get(round, "nothing"),16)
	#Kr=int(constantmap_right.get(round, "nothing"),16)
	
	#s
	s=shiftmap_left.get(round*16+j,"nothing")
        #sr=shiftmap_right.get(round*16+j,"nothing")
	# print 'round {} j {}, K {}, s {}, r {}'.format(round,j,K,s,r)

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
		A_out=(A_out+dfunction1(B,C,D))%mask
	elif f==2:
                A_out=(A_out+dfunction2(B,C,D))%mask
        elif f==3:
                A_out=(A_out+dfunction3(B,C,D))%mask
        elif f==4:
                A_out=(A_out+dfunction4(B,C,D))%mask
        elif f==5:
                A_out=(A_out+dfunction5(B,C,D))%mask
	A_out000=(A_out+X)%mask
	A_out00=(A_out000+K)%mask
	A_out0=ROL(A_out00,s)%mask
	A_out1=(A_out0+E)%mask
	# if K==2840853838:
	# 	# print 'f {} {} {} {} {}'.format(f,B,C,D,hex(dfunction5(B,C,D)%mask))
	# 	# print 'A {}'.format(hex(A))
	# 	# print 'A_out4 {}'.format(hex((A+dfunction5(B,C,D))%mask))
	# 	print 'A_out3 {}'.format(hex(A_out000))
	# 	print 'A_out2 {}'.format(hex(A_out00))
	# 	print 'A_out1 {}'.format(hex(A_out0))
	# 	print 'A_out {}'.format(hex(A_out1))

	C_out=ROL(C,10)%mask
	return A_out1%mask,C_out%mask