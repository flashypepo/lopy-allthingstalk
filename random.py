import crypto

def Random():
   r = crypto.getrandbits(32)
   return ((r[0]<<24)+(r[1]<<16)+(r[2]<<8)+r[3])/4294967295.0

def randint(rfrom, rto):
   return Random()*(rto-rfrom)+rfrom
