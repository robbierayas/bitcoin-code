# Classical Algorithms for the Elliptic Curve Discrete Logarithm Problem (ECDLP)

This document explains classical (non-quantum) algorithms for solving the discrete logarithm problem on elliptic curves.

## The Problem

**Given:** Public key Q and generator point G on an elliptic curve
**Find:** Private key d such that Q = d * G

This is the foundation of ECDSA security. If you can solve this efficiently, you can steal Bitcoin.

---

## Algorithm Summary

| Algorithm | Time | Space | When to Use |
|-----------|------|-------|-------------|
| Brute Force | O(n) | O(1) | Never (baseline comparison only) |
| Baby-step Giant-step | O(sqrt(n)) | O(sqrt(n)) | General case, memory available |
| Pollard's Rho | O(sqrt(n)) | O(1) | General case, memory constrained |
| Pollard's Kangaroo | O(sqrt(W)) | O(1) | Key known to be in range of width W |
| Pohlig-Hellman | O(sum e_i * sqrt(p_i)) | varies | Group order has small prime factors |

Where n = group order N, and for Pohlig-Hellman, N = prod(p_i^e_i).

---

## 1. Brute Force

**Time:** O(n)
**Space:** O(1)

The simplest approach: try every possible private key.

```
for d = 1 to N-1:
    if d * G == Q:
        return d
```

**Analysis:**
- Must try n/2 keys on average
- For Bitcoin (n = 2^256): need 2^255 operations
- At 10^18 ops/sec: 10^58 years
- Completely infeasible

**Use case:** Only for tiny examples (4-bit keys).

---

## 2. Baby-step Giant-step (BSGS)

**Time:** O(sqrt(n))
**Space:** O(sqrt(n))

A time-space tradeoff using meet-in-the-middle.

**Algorithm:**
```
m = ceil(sqrt(N))

# Baby steps: build lookup table
for j = 0 to m-1:
    table[j * G] = j

# Giant steps: search for collision
gamma = Q
for i = 0 to m-1:
    if gamma in table:
        j = table[gamma]
        return i * m + j
    gamma = gamma - m * G
```

**Why it works:**
- If d = i*m + j where 0 <= j < m, then:
- Q = d*G = (i*m + j)*G
- Q - i*m*G = j*G
- We precompute all j*G, then search for Q - i*m*G

**Analysis:**
- Baby steps: m point multiplications, m table entries
- Giant steps: up to m iterations
- Total: O(sqrt(n)) time and space
- For Bitcoin: 2^128 operations and 2^128 storage
- Still infeasible, but squared improvement

---

## 3. Pollard's Rho

**Time:** O(sqrt(n)) expected
**Space:** O(1)

Uses random walks and cycle detection to find collisions.

**Core idea:**
- Define a pseudorandom walk on the group
- Two walks starting from different points will eventually collide
- Birthday paradox: collision expected after O(sqrt(n)) steps
- From collision, extract the discrete log

**Algorithm (simplified):**
```
# Random walk function
def step(X, a, b):
    # Partition based on X
    if X in S0: return (X + Q, a, b + 1)
    if X in S1: return (2*X, 2*a, 2*b)
    if X in S2: return (X + G, a + 1, b)

# Tortoise and hare
X_slow = X_fast = random_start
a_slow, b_slow = initial_coefficients
a_fast, b_fast = initial_coefficients

while True:
    # Tortoise: one step
    X_slow, a_slow, b_slow = step(X_slow, a_slow, b_slow)

    # Hare: two steps
    X_fast, a_fast, b_fast = step(X_fast, a_fast, b_fast)
    X_fast, a_fast, b_fast = step(X_fast, a_fast, b_fast)

    if X_slow == X_fast:
        # Collision: a1*G + b1*Q = a2*G + b2*Q
        # (a1 - a2)*G = (b2 - b1)*Q = (b2 - b1)*d*G
        # d = (a1 - a2) / (b2 - b1) mod N
        return (a_slow - a_fast) * inverse(b_fast - b_slow) mod N
```

**Analysis:**
- Expected O(sqrt(pi*n/2)) steps
- Only O(1) memory (just current state)
- Preferred over BSGS when memory is limited
- For Bitcoin: still 2^128 operations

---

## 4. Pollard's Kangaroo (Lambda)

**Time:** O(sqrt(W)) where W = b - a
**Space:** O(1)

Optimal when the private key is known to lie in a bounded interval [a, b].

**Scenario:** You know d is between a and b (perhaps from a side-channel leak).

**Algorithm:**
```
W = b - a  # Range width
m = sqrt(W)  # Mean jump size

# TAME kangaroo: starts at known point b*G
tame_pos = b * G
tame_dist = 0

# Let tame kangaroo hop, recording its trail
for _ in range(O(sqrt(W))):
    jump = pseudorandom_jump(tame_pos)
    tame_pos = tame_pos + jump * G
    tame_dist += jump
    record(tame_pos, tame_dist)

# WILD kangaroo: starts at target Q = d*G
wild_pos = Q
wild_dist = 0

# Wild kangaroo hops until hitting tame's trail
while wild_pos not in tame_trail:
    jump = pseudorandom_jump(wild_pos)
    wild_pos = wild_pos + jump * G
    wild_dist += jump

# At collision:
# tame: (b + tame_dist) * G
# wild: (d + wild_dist) * G
# These are equal, so: d = b + tame_dist - wild_dist
```

**Why "kangaroo"?**
- Both kangaroos take random jumps across the group
- When they land on the same point, we can compute d
- Like kangaroos meeting at a watering hole

**Analysis:**
- Expected O(sqrt(W)) steps for each kangaroo
- Only stores the tame kangaroo's trail
- If W << N, much faster than general algorithms

**Critical insight for Bitcoin:**

| Bits Unknown | W | Kangaroo Steps | Feasible? |
|--------------|---|----------------|-----------|
| 256 | 2^256 | 2^128 | No |
| 128 | 2^128 | 2^64 | Borderline (years) |
| 64 | 2^64 | 2^32 | Yes (hours) |
| 32 | 2^32 | 2^16 | Yes (instant) |

This is why partial key leakage is dangerous!

---

## 5. Pohlig-Hellman

**Time:** O(sum of e_i * sqrt(p_i)) where N = prod(p_i^e_i)
**Space:** Varies

Exploits the factorization of the group order.

**Key insight:** If N = p1^e1 * p2^e2 * ... * pk^ek, we can:
1. Solve d mod p_i^e_i for each prime power (smaller subproblems)
2. Combine using Chinese Remainder Theorem

**Algorithm:**
```
for each prime power p^e dividing N:
    # Move to subgroup of order p^e
    h = (N / p^e) * G      # Generator of order p^e
    Q' = (N / p^e) * Q     # Target in subgroup

    # Solve d mod p^e using BSGS (only sqrt(p) work!)
    d_mod_pe = bsgs(Q', h, p^e)

    partial_results.append((d_mod_pe, p^e))

# Combine with CRT
d = chinese_remainder_theorem(partial_results)
```

**Example:**
```
N = 12 = 2^2 * 3

Step 1: Solve d mod 4
  - Subgroup of order 4
  - Only 4 possibilities
  - Find d = 3 (mod 4)

Step 2: Solve d mod 3
  - Subgroup of order 3
  - Only 3 possibilities
  - Find d = 2 (mod 3)

Step 3: CRT
  - d = 3 (mod 4)
  - d = 2 (mod 3)
  - Solution: d = 11 (mod 12)

Work: 4 + 3 = 7 operations
BSGS would need: sqrt(12) ~ 3.5 operations per iteration
Brute force: 12 operations
```

**When Pohlig-Hellman is devastating:**
```
N = 2^32

BSGS: sqrt(2^32) = 2^16 = 65,536 operations
Pohlig-Hellman: 32 * sqrt(2) ~ 45 operations!

That's a 1000x speedup!
```

**Why Bitcoin is safe:**
```
secp256k1 order N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

This is PRIME. No factorization to exploit.
Pohlig-Hellman provides zero speedup.
```

Curve designers specifically choose prime-order groups to prevent this attack.

---

## 6. Comparison for Bitcoin (secp256k1)

Bitcoin uses the secp256k1 curve with:
- Prime field: p = 2^256 - 2^32 - 977
- Group order: N = a 256-bit prime
- Security level: 128 bits (sqrt of 256)

| Algorithm | Operations Needed | Time at 10^18 ops/sec |
|-----------|-------------------|----------------------|
| Brute Force | 2^256 | 10^58 years |
| BSGS | 2^128 | 10^19 years |
| Pollard's Rho | 2^128 | 10^19 years |
| Kangaroo (full) | 2^128 | 10^19 years |
| Pohlig-Hellman | 2^128 (N is prime) | 10^19 years |

**All classical algorithms hit the sqrt(n) = 2^128 barrier.**

---

## 7. The Quantum Threat

Shor's algorithm solves ECDLP in O(n^3) = O(256^3) ~ 16 million operations.

| Approach | Operations | Feasibility |
|----------|------------|-------------|
| Best classical | 2^128 | Impossible |
| Shor's algorithm | ~10^7 | Minutes (with quantum computer) |

**Gap:** ~10^30x difference

This gap exists because:
- Classical: must check candidates one by one (or meet-in-middle for sqrt)
- Quantum: superposition checks ALL candidates simultaneously, interference cancels wrong answers

**Current status:**
- Need ~2000-4000 logical qubits
- Each logical qubit needs ~1000-10000 physical qubits (error correction)
- Current: ~1000 noisy physical qubits
- Timeline: 10-30 years

---

## 8. Practical Attack Scenarios

### Scenario A: Full 256-bit key, no information
- Best attack: Pollard's Rho (O(2^128), O(1) space)
- Feasibility: **Impossible**

### Scenario B: Weak RNG reduced entropy to 64 bits
- Best attack: Kangaroo with W = 2^64
- Operations: 2^32
- Feasibility: **Hours to days**

### Scenario C: Side-channel leaked 192 bits
- Remaining: 64 unknown bits
- Best attack: Kangaroo with W = 2^64
- Feasibility: **Hours to days**

### Scenario D: Nonce reuse in signatures
- Best attack: Direct algebraic recovery
- Operations: O(1)
- Feasibility: **Instant**

### Scenario E: Group order is 2^64 (hypothetical weak curve)
- Best attack: Pohlig-Hellman
- Operations: 64 * sqrt(2) ~ 90
- Feasibility: **Instant**

---

## 9. Implementation Files

In this project's `rollback/` directory:

| File | Algorithms |
|------|------------|
| `bruteECDSA4bitMechanism.py` | Brute force, BSGS, Pollard's Rho, Lookup table, Nonce recovery |
| `kangarooECDSA4bitMechanism.py` | Pollard's Kangaroo for bounded ranges |
| `pohligHellmanECDSA4bitMechanism.py` | Pohlig-Hellman with CRT |
| `shorECDSA4bitMechanism.py` | Classical simulation of Shor's algorithm |

All implementations work on the 4-bit educational curve (N=19, prime order).

---

## 10. References

- Shanks, D. "Class number, a theory of factorization, and genera" (1971) - Baby-step Giant-step
- Pollard, J.M. "Monte Carlo methods for index computation (mod p)" (1978) - Rho algorithm
- Pollard, J.M. "Kangaroos, Monopoly and Discrete Logarithms" (2000) - Kangaroo algorithm
- Pohlig, S. and Hellman, M. "An improved algorithm for computing logarithms" (1978)
- Shor, P. "Algorithms for quantum computation" (1994) - Quantum algorithm

---

## 11. Modular Inverse and Bit-Level Operations

For detailed explanation of:
- Why mod_inverse destroys bit relationships (the division problem)
- Mathematical vs bit-level reversibility
- The slope calculation chain in point operations

**See [bitUtils.md](bitUtils.md)**

Quick summary:
- mod_inverse is O(log p) and mathematically self-reversing: (a^(-1))^(-1) = a
- But division has NO bit-by-bit pattern - each output bit depends on ALL input bits
- ECDLP security comes from losing d's binary representation through many operations, not from mod_inverse being "hard"

---

## Summary

1. **All classical algorithms are O(sqrt(n)) or worse** for properly chosen curves
2. **Bitcoin's secp256k1 is secure** - prime order defeats Pohlig-Hellman, and 2^128 operations is infeasible
3. **Partial key leakage is dangerous** - Kangaroo can exploit bounded ranges
4. **Quantum computers will break ECDSA** - but we have 10-30 years (probably)
5. **Choose curves carefully** - prime order is essential for security
6. **Mod inverse is NOT the bottleneck** - O(log p) both directions, self-reversing
