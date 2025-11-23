"""
Brute force RIPEMD-160 rollback mechanism.

This module implements a brute force approach to reverse RIPEMD-160 hash operations.
This is experimental cryptographic research code.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography import base58Utils
from rollback.rollbackMechanism import RollbackMechanism


# RIPEMD-160 Constants and Mappings
ordermap = {
    0: 7, 1: 4, 2: 13, 3: 1, 4: 10, 5: 6, 6: 15, 7: 3,
    8: 12, 9: 0, 10: 9, 11: 5, 12: 2, 13: 14, 14: 11, 15: 8
}

functionmap_left = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
functionmap_right = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1}

constantmap_left = {
    0: '00000000', 1: '5A827999', 2: '6ED9EBA1',
    3: '8F1BBCDC', 4: 'A953FD4E'
}
constantmap_right = {
    0: '50A28BE6', 1: '5C4DD124', 2: '6D703EF3',
    3: '7A6D76E9', 4: '00000000'
}

shiftmap_left = {
    0: 11, 1: 14, 2: 15, 3: 12, 4: 5, 5: 8, 6: 7, 7: 9, 8: 11, 9: 13, 10: 14, 11: 15, 12: 6, 13: 7, 14: 9, 15: 8,
    16: 7, 17: 6, 18: 8, 19: 13, 20: 11, 21: 9, 22: 7, 23: 15, 24: 7, 25: 12, 26: 15, 27: 9, 28: 11, 29: 7, 30: 13, 31: 12,
    32: 11, 33: 13, 34: 6, 35: 7, 36: 14, 37: 9, 38: 13, 39: 15, 40: 14, 41: 8, 42: 13, 43: 6, 44: 5, 45: 12, 46: 7, 47: 5,
    48: 11, 49: 12, 50: 14, 51: 15, 52: 14, 53: 15, 54: 9, 55: 8, 56: 9, 57: 14, 58: 5, 59: 6, 60: 8, 61: 6, 62: 5, 63: 12,
    64: 9, 65: 15, 66: 5, 67: 11, 68: 6, 69: 8, 70: 13, 71: 12, 72: 5, 73: 12, 74: 13, 75: 14, 76: 11, 77: 8, 78: 5, 79: 6
}

shiftmap_right = {
    0: 8, 1: 9, 2: 9, 3: 11, 4: 13, 5: 15, 6: 15, 7: 5, 8: 7, 9: 7, 10: 8, 11: 11, 12: 14, 13: 14, 14: 12, 15: 6,
    16: 9, 17: 13, 18: 15, 19: 7, 20: 12, 21: 8, 22: 9, 23: 11, 24: 7, 25: 7, 26: 12, 27: 7, 28: 6, 29: 15, 30: 13, 31: 11,
    32: 9, 33: 7, 34: 15, 35: 11, 36: 8, 37: 6, 38: 6, 39: 14, 40: 12, 41: 13, 42: 5, 43: 14, 44: 13, 45: 13, 46: 7, 47: 5,
    48: 15, 49: 5, 50: 8, 51: 11, 52: 14, 53: 14, 54: 6, 55: 14, 56: 6, 57: 9, 58: 12, 59: 9, 60: 12, 61: 5, 62: 15, 63: 8,
    64: 8, 65: 5, 66: 12, 67: 9, 68: 12, 69: 5, 70: 14, 71: 6, 72: 8, 73: 13, 74: 6, 75: 5, 76: 15, 77: 13, 78: 11, 79: 11
}

rho = {
    0: 7, 1: 4, 2: 13, 3: 1, 4: 10, 5: 6, 6: 15, 7: 3,
    8: 12, 9: 0, 10: 9, 11: 5, 12: 2, 13: 14, 14: 11, 15: 8
}

wordselect_left = {
    0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
    16: 7, 17: 4, 18: 13, 19: 1, 20: 10, 21: 6, 22: 15, 23: 3, 24: 12, 25: 0, 26: 9, 27: 5, 28: 2, 29: 14, 30: 11, 31: 8,
    32: 3, 33: 10, 34: 14, 35: 4, 36: 9, 37: 15, 38: 8, 39: 1, 40: 2, 41: 7, 42: 0, 43: 6, 44: 13, 45: 11, 46: 5, 47: 12,
    48: 1, 49: 9, 50: 11, 51: 10, 52: 0, 53: 8, 54: 12, 55: 4, 56: 13, 57: 3, 58: 7, 59: 15, 60: 14, 61: 5, 62: 6, 63: 2,
    64: 4, 65: 0, 66: 5, 67: 9, 68: 7, 69: 12, 70: 2, 71: 10, 72: 14, 73: 1, 74: 3, 75: 8, 76: 11, 77: 6, 78: 15, 79: 13
}

wordselect_right = {
    0: 5, 1: 14, 2: 7, 3: 0, 4: 9, 5: 2, 6: 11, 7: 4, 8: 13, 9: 6, 10: 15, 11: 8, 12: 1, 13: 10, 14: 3, 15: 12,
    16: 6, 17: 11, 18: 3, 19: 7, 20: 0, 21: 13, 22: 5, 23: 10, 24: 14, 25: 15, 26: 8, 27: 12, 28: 4, 29: 9, 30: 1, 31: 2,
    32: 15, 33: 5, 34: 1, 35: 3, 36: 7, 37: 14, 38: 6, 39: 9, 40: 11, 41: 8, 42: 12, 43: 2, 44: 10, 45: 0, 46: 4, 47: 13,
    48: 8, 49: 6, 50: 4, 51: 1, 52: 3, 53: 11, 54: 15, 55: 0, 56: 5, 57: 12, 58: 2, 59: 13, 60: 9, 61: 7, 62: 10, 63: 14,
    64: 12, 65: 15, 66: 10, 67: 4, 68: 1, 69: 5, 70: 8, 71: 7, 72: 6, 73: 2, 74: 13, 75: 14, 76: 0, 77: 3, 78: 9, 79: 11
}

# Initial hash values
A0 = int('67452301', 16)
B0 = int('efcdab89', 16)
C0 = int('98badcfe', 16)
D0 = int('10325476', 16)
E0 = int('c3d2e1f0', 16)

# Overflow mask 2^32
mask = 4294967296


class BruteRipeMD160Mechanism(RollbackMechanism):
    """
    Brute force mechanism for attempting to reverse RIPEMD-160 operations.

    This is experimental cryptographic research attempting to work backwards
    from a Bitcoin address hash to find intermediate values.
    """

    def __init__(self, address, max_iterations=None, progress_interval=1000):
        """
        Initialize the brute force RIPEMD-160 mechanism.

        Args:
            address: Bitcoin address to attempt rollback on
            max_iterations: Maximum iterations before stopping (None = unlimited)
            progress_interval: How often to report progress (every N iterations)
        """
        super().__init__(address)
        self.address = address
        self.verbose = True
        self.max_iterations = max_iterations
        self.progress_interval = progress_interval

        # Stats tracking
        self.stats = {
            'total_iterations': 0,
            'findX_calls': 0,
            'brute_force_attempts': 0,
            'X_values_found': 0,
            'stopped_early': False,
            'stop_reason': None
        }
        self.interrupted = False

    def should_stop(self):
        """Check if we should stop (max iterations or interrupted)."""
        if self.interrupted:
            self.stats['stopped_early'] = True
            self.stats['stop_reason'] = 'interrupted'
            return True

        if self.max_iterations and self.stats['total_iterations'] >= self.max_iterations:
            self.stats['stopped_early'] = True
            self.stats['stop_reason'] = 'max_iterations'
            return True

        return False

    def print_stats(self):
        """Print current statistics."""
        print("\n" + "=" * 70)
        print("CURRENT STATISTICS")
        print("=" * 70)
        print(f"Total Iterations:       {self.stats['total_iterations']:,}")
        print(f"findX_r Calls:          {self.stats['findX_calls']:,}")
        print(f"Brute Force Attempts:   {self.stats['brute_force_attempts']:,}")
        print(f"X Values Found:         {self.stats['X_values_found']}")

        if self.stats['stopped_early']:
            print(f"\nStopped Early:          Yes")
            print(f"Stop Reason:            {self.stats['stop_reason']}")

        if self.max_iterations:
            progress_pct = (self.stats['total_iterations'] / self.max_iterations) * 100
            print(f"Progress:               {progress_pct:.1f}%")

        print("=" * 70)

    def report_progress(self):
        """Report progress if at interval."""
        if self.stats['total_iterations'] % self.progress_interval == 0:
            if self.verbose:
                print(f"  [Progress] Iterations: {self.stats['total_iterations']:,}, "
                      f"findX calls: {self.stats['findX_calls']:,}, "
                      f"X found: {self.stats['X_values_found']}")

    def run(self):
        """
        Execute the brute force rollback attempt.

        Returns:
            Dictionary containing intermediate values found during rollback
        """
        if self.verbose:
            print(f'Rollback address {self.address}')

        basedecode = base58Utils.base58CheckDecode(self.address)
        if self.verbose:
            print(f'Rollback basedecode {basedecode}')

        hex_data = basedecode.hex()
        if self.verbose:
            print(f'Rollback hex {hex_data}')

        Af_hex = hex_data[:8]
        Bf_hex = hex_data[8:16]
        Cf_hex = hex_data[16:24]
        Df_hex = hex_data[24:32]
        Ef_hex = hex_data[32:40]

        if self.verbose:
            print(f'hnew {Af_hex} {Bf_hex} {Cf_hex} {Df_hex} {Ef_hex}')
            print('TO DO un-add final values')

        # Known intermediate values (hardcoded for testing)
        Al = int('82a24ea5', 16)
        Bl = int('11e8ef41', 16)
        Cl = int('e109aea8', 16)
        Dl = int('e3474402', 16)
        El = int('302cc6dc', 16)

        Ar = int('5592219f', 16)
        Br = int('4eb93ee3', 16)
        Cr = int('a91d7fa6', 16)
        Dr = int('0c8673c2', 16)
        Er = int('ac4b8c30', 16)

        if self.verbose:
            print('')
            print(f'h_left 15 {hex(Al)} {hex(Bl)} {hex(Cl)} {hex(Dl)} {hex(El)}')
            print(f'h_right 15 {hex(Ar)} {hex(Br)} {hex(Cr)} {hex(Dr)} {hex(Er)}')
            print('')

        X = ['' for i in range(8)] + [
            int('00000080', 16), int('00000000', 16), int('00000000', 16),
            int('00000000', 16), int('00000000', 16), int('00000000', 16),
            int('00000100', 16), int('00000000', 16)
        ]
        Xrr = ['' for i in range(8)] + [
            int('00000080', 16), int('00000000', 16), int('00000000', 16),
            int('00000000', 16), int('00000000', 16), int('00000000', 16),
            int('00000100', 16), int('00000000', 16)
        ]

        for round in range(4, 3, -1):
            if self.should_stop():
                break

            if self.verbose:
                print(f'round {round}')

            for j in range(15, 10, -1):
                if self.should_stop():
                    break

                self.stats['total_iterations'] += 1
                self.report_progress()

                if self.verbose:
                    print(f'j {j}')

                # Left side
                Al, Bl, Cl, Dl, El, Xl = self._rcompression(
                    Al, Bl, Cl, Dl, El,
                    functionmap_left.get(round, "nothing"),
                    X, round, j
                )

                if self.verbose:
                    print('')
                    print(f'h_left {j-1} {hex(Al)} {hex(Bl)} {hex(Cl)} {hex(Dl)} {hex(El)}')
                    print(f'X {X}')

        self.result = {
            'X': X,
            'h_left': {'A': Al, 'B': Bl, 'C': Cl, 'D': Dl, 'E': El},
            'h_right': {'A': Ar, 'B': Br, 'C': Cr, 'D': Dr, 'E': Er},
            'stats': self.stats.copy()
        }

        # Print final stats if verbose
        if self.verbose:
            self.print_stats()

        return self.result

    def _rcompression(self, A, B, C, D, E, f, X, round, j):
        """Reverse compression function."""
        r = wordselect_left.get(round * 16 + j, "nothing")
        K = int(constantmap_left.get(round, "nothing"), 16)
        s = shiftmap_left.get(round * 16 + j, "nothing")

        X_out = X[r]

        if X[r] != '':
            A_out, C_out, X_out = self._doperation(A, B, C, D, E, f, X[r], K, s)
            if X[r] != X_out:
                print(f'Xr!=Xout {X[r]} {X_out}')
        else:
            A_out, C_out, X_out = self._findX_r(A, B, C, D, E, f, X, r, K, s, round, j)
            X[r] = X_out

        D = E
        B = C
        E = A
        A = A_out
        C = C_out

        return A, B, C, D, E, X_out

    def _findX_r(self, A, B, C, D, E, f, X, r, K, s, round, j):
        """Find X value through brute force."""
        self.stats['findX_calls'] += 1

        if self.verbose:
            print('          findX_r')

        C_out = self._ROR(D, 10) % mask
        A_out = B
        A_out1 = (A_out - A) % mask
        A_out2 = self._ROR(A_out1, s) % mask
        A_out3 = (A_out2 - K) % mask

        print('         begin finding X')
        Cl = C_out
        Dl = E
        Bl = C
        El = A

        foundX = False
        i_A = 3785517728
        while not foundX and not self.should_stop():
            Al = i_A

            All, Bll, Cll, Dll, Ell, Xl2 = self._rcompression(Al, Bl, Cl, Dl, El, f, X, round, j - 1)

            if self.verbose:
                print('         check value')
            Ac, Bc, Cc, Dc, Ec = self._compression(All, Bll, Cll, Dll, Ell, f, Xl2, round, j - 1)

            i_X = 0
            while i_X < 4294967296 and not self.should_stop():
                self.stats['brute_force_attempts'] += 1
                Xl = i_X
                Af, Bf, Cf, Df, Ef = self._compression(Ac, Bc, Cc, Dc, Ec, f, Xl, round, j)

                if Bf == B:
                    foundX = True
                    X_out = Xl
                    self.stats['X_values_found'] += 1
                    i_X = 5000000000
                    A_out4 = (A_out3 - Xl) % mask
                    if self.verbose:
                        print('         bruteforce worked')
                i_X = i_X + 1

            i_A = i_A + 1
            if i_A == 3785517729:
                foundX = True
                if self.verbose:
                    print('         bruteforce done')

        if f == 1:
            A_out4 = (A_out4 - self._dfunction1(C, C_out, E)) % mask
        elif f == 2:
            A_out4 = (A_out4 - self._dfunction2(C, C_out, E)) % mask
        elif f == 3:
            A_out4 = (A_out4 - self._dfunction3(C, C_out, E)) % mask
        elif f == 4:
            A_out4 = (A_out4 - self._dfunction4(C, C_out, E)) % mask
        elif f == 5:
            A_out4 = (A_out4 - self._dfunction5(C, C_out, E)) % mask

        return A_out4 % mask, C_out % mask, X_out

    def _doperation(self, A, B, C, D, E, f, X, K, s):
        """Decompress operation."""
        C_out = self._ROR(D, 10) % mask
        A_out = B
        A_out1 = (A_out - A) % mask
        A_out2 = self._ROR(A_out1, s) % mask
        A_out3 = (A_out2 - K) % mask
        A_out4 = (A_out3 - X) % mask

        if f == 1:
            A_out4 = (A_out4 - self._dfunction1(C, C_out, E)) % mask
        elif f == 2:
            A_out4 = (A_out4 - self._dfunction2(C, C_out, E)) % mask
        elif f == 3:
            A_out4 = (A_out4 - self._dfunction3(C, C_out, E)) % mask
        elif f == 4:
            A_out4 = (A_out4 - self._dfunction4(C, C_out, E)) % mask
        elif f == 5:
            A_out4 = (A_out4 - self._dfunction5(C, C_out, E)) % mask

        return A_out4 % mask, C_out % mask, X

    def _compression(self, A, B, C, D, E, f, X, round, j):
        """Forward compression function."""
        r = wordselect_left.get(round * 16 + j, "nothing")
        K = int(constantmap_left.get(round, "nothing"), 16)
        s = shiftmap_left.get(round * 16 + j, "nothing")

        A_out, C_out = self._operation(A, B, C, D, E, f, X, K, s)
        A = E % mask
        C = B % mask
        E = D % mask
        B = A_out
        D = C_out
        return A, B, C, D, E

    def _operation(self, A, B, C, D, E, f, X, K, s):
        """Forward operation."""
        A_out = A
        if f == 1:
            A_out = (A_out + self._dfunction1(B, C, D)) % mask
        elif f == 2:
            A_out = (A_out + self._dfunction2(B, C, D)) % mask
        elif f == 3:
            A_out = (A_out + self._dfunction3(B, C, D)) % mask
        elif f == 4:
            A_out = (A_out + self._dfunction4(B, C, D)) % mask
        elif f == 5:
            A_out = (A_out + self._dfunction5(B, C, D)) % mask

        A_out000 = (A_out + X) % mask
        A_out00 = (A_out000 + K) % mask
        A_out0 = self._ROL(A_out00, s) % mask
        A_out1 = (A_out0 + E) % mask

        C_out = self._ROL(C, 10) % mask
        return A_out1 % mask, C_out % mask

    # RIPEMD-160 mixing functions
    def _dfunction1(self, B, C, D):
        binB = int(bin(B)[2:], 2)
        binC = int(bin(C)[2:], 2)
        binD = int(bin(D)[2:], 2)
        return binB ^ binC ^ binD

    def _dfunction2(self, B, C, D):
        binB = int(bin(B)[2:], 2)
        binC = int(bin(C)[2:], 2)
        binD = int(bin(D)[2:], 2)
        return (binB & binC) | (~binB & binD)

    def _dfunction3(self, B, C, D):
        binB = int(bin(B)[2:], 2)
        binC = int(bin(C)[2:], 2)
        binD = int(bin(D)[2:], 2)
        return (binB | ~binC) ^ binD

    def _dfunction4(self, B, C, D):
        binB = int(bin(B)[2:], 2)
        binC = int(bin(C)[2:], 2)
        binD = int(bin(D)[2:], 2)
        return (binB & binD) | (binC & ~binD)

    def _dfunction5(self, B, C, D):
        binB = int(bin(B)[2:], 2)
        binC = int(bin(C)[2:], 2)
        binD = int(bin(D)[2:], 2)
        return binB ^ (binC | ~binD)

    # Bit rotation functions
    def _ROL(self, C, s):
        """Rotate left."""
        C_rot = (C << s) | (C >> 32 - s)
        return C_rot

    def _ROR(self, C, s):
        """Rotate right."""
        C_rot = (C >> s) | (C << 32 - s)
        return C_rot
