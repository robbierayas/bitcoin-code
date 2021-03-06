import os, math

def makehex(value,size=8):
    value = hex(value)[2:]
    if value[-1] == 'L':
        value = value[0:-1]
    while len(value)<size:
        value = '0' + value
    return value

def makebin(value,size=32):
    value = bin(value)[2:]
    while len(value)<size:
        value = '0' + value
    return value

def ROL(value,n):
    return (value << n) | (value >> 32-n)

def little_end(string,base = 16):
    t = ''
    if base == 2:
        s= 8
    if base == 16:
        s = 2
    for x in range(len(string)/s):
        t = string[s*x:s*(x+1)] + t
    return t

def F(x,y,z,round):
    if round<16:
        return x ^ y ^ z
    elif 16<=round<32:
        return (x & y) | (~x & z)
    elif 32<=round<48:
        return (x | ~y) ^ z
    elif 48<=round<64:
        return (x & z) | (y & ~z)
    elif 64<=round:
        return x ^ (y | ~z)

def RIPEMD160(data):

# constants
    h0 = 0x67452301; h1 = 0xEFCDAB89; h2 = 0x98BADCFE;h3 = 0x10325476; h4 = 0xC3D2E1F0

    k  = [0, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]
    kk = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9,0]
    s =     [   11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,
            7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,
            11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,
            11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,
            9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6]
    ss=     [   8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,
            9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,
            9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,
            15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,
            8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11]
    r= range(16) + [    7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
                3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
                1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
                4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]
    rr =    [   5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
            6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
            15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
            8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
            12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]   

    # md4 padding + preprocessing
    temp = ''
    for x in data:
        temp += makebin(int(x,16),4)
    length = len(temp)%2**64
    temp +='1'
    while len(temp)%512!=448:
        temp+='0'
    input = temp
    temp = makebin(length,64)
    bit_length=''
    for x in range(len(input)/32):
        bit_length += little_end(temp[32*x:32*(x+1)],2)
    input += bit_length[32:]+bit_length[:32]
    t = len(input)/512
    # the rounds
    for i in range(t):

            # i called the parallel round variables 2x the other round variable: a -> aa
        a = aa = h0; b = bb = h1; c = cc = h2; d = dd = h3; e = ee = h4
        X = input[512*i:512*(i+1)]
        X = [int(little_end(X[32*x:32*(x+1)],2),2) for x in range(16)]
        for j in range(80):
            T = (ROL((a+ F(b, c, d, j) + X[r[j]] + k[j/16])%2**32,s[j])+e)%2**32
            c = ROL(c, 10)%2**32
            a = e; e = d; d = c; c = b; b = T
            T = (ROL((aa+ F(bb,cc,dd,79-j) + X[rr[j]] + kk[j/16] )%2**32,ss[j])+ee)%2**32
            cc = ROL(cc,10)%2**32
            aa = ee; ee = dd; dd = cc; cc = bb; bb = T
        T  = (h1+c+dd)%2**32
        h1 = (h2+d+ee)%2**32
        h2 = (h3+e+aa)%2**32
        h3 = (h4+a+bb)%2**32
        h4 = (h0+b+cc)%2**32
        h0 = T
    return little_end(makehex(h0))+little_end(makehex(h1))+little_end(makehex(h2))+little_end(makehex(h3))+little_end(makehex(h4))
data = RIPEMD160('')
print data,data =='9c1185a5c5e9fc54612808977ee8f548b2258d31'