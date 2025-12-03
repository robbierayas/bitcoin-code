# Shor's Algorithm for Elliptic Curve Discrete Logarithm

## Overview

Shor's algorithm is a quantum algorithm that solves the discrete logarithm problem
in polynomial time. For ECDSA, this means breaking the security of Bitcoin's
cryptography - given a public key Q and generator G, find the private key d where Q = d*G.

**Classical complexity:** O(sqrt(N)) with best algorithms (Pollard's rho)
**Quantum complexity:** O(n^3) where n = log2(N) - exponentially faster!

---

## The Quantum Fourier Transform (QFT)

### Mathematical Definition

The QFT transforms a quantum state from the computational basis to the frequency basis:

```
                 N-1
QFT|j> = (1/sqrt(N)) * SUM  exp(2*pi*i*j*k/N) * |k>
                 k=0
```

Or in matrix form for an N-dimensional system:

```
         [ 1      1        1         ...   1           ]
         [ 1      w        w^2       ...   w^(N-1)     ]
QFT = 1/sqrt(N) * [ 1      w^2      w^4       ...   w^(2(N-1)) ]
         [ ...    ...      ...       ...   ...         ]
         [ 1      w^(N-1)  w^(2(N-1))  ...   w^((N-1)^2)]

where w = exp(2*pi*i/N) is the N-th root of unity
```

### Key Properties

1. **Unitary:** QFT^(-1) = QFT^(dagger) (reversible)
2. **Period Detection:** If |psi> has period r, QFT|psi> has peaks at multiples of N/r
3. **Efficient:** O(n^2) quantum gates for n qubits (vs O(N*log(N)) classical FFT on N values)

### QFT for 4 Qubits (N=16)

For our 4-bit simulation with N=19 (group order), the QFT would be:

```
QFT|j> = (1/sqrt(19)) * SUM_{k=0}^{18} exp(2*pi*i*j*k/19) * |k>
```

For example, QFT|1> (the "1" frequency):
```
QFT|1> = (1/sqrt(19)) * (|0> + w|1> + w^2|2> + ... + w^18|18>)
where w = exp(2*pi*i/19)
```

---

## Shor's Algorithm for ECDLP

### The Problem

Given: Public key Q, Generator G, Group order N
Find: Private key d such that Q = d*G (mod N)

### The Algorithm Steps

**Step 1: Superposition**
```
|psi_1> = (1/sqrt(N)) * SUM_{x=0}^{N-1} |x>|0>
```
Create equal superposition of all possible values in the first register.

**Step 2: Oracle Application**
```
|psi_2> = (1/sqrt(N)) * SUM_{x=0}^{N-1} |x>|x*G>
```
Compute f(x) = x*G for ALL x values simultaneously (quantum parallelism).
The second register now holds the curve point x*G.

**Step 3: Hidden Subgroup Problem**
The key insight is that we're looking for x where x*G = Q.
This means x = d (the private key we want).

For ECDLP on a cyclic group, we use a variation:
- Create |x>|y>|x*G + y*Q>
- Look for (x,y) pairs where x*G + y*Q = O (point at infinity)
- This happens when x + y*d = 0 (mod N), i.e., x = -y*d (mod N)
- The period reveals d!

**Step 4: Quantum Fourier Transform**
```
|psi_3> = QFT_x (x) QFT_y |psi_2>
```
Apply QFT to detect the periodicity. The hidden subgroup structure
causes constructive interference at values related to d.

**Step 5: Measurement**
Measure the system. With high probability, we get a value m where:
```
m/N ~= k/r  for some integers k, r
```
Here r is related to the period, which encodes d.

**Step 6: Classical Post-Processing**
Use continued fractions to extract r from m/N, then compute d.

---

## Why This Actually Works (The Math)

### Period Finding View

Consider the function f(a,b) = a*G + b*Q over pairs (a,b).
- f(a,b) = f(a',b') iff a*G + b*Q = a'*G + b'*Q
- This means (a-a')*G = (b'-b)*Q = (b'-b)*d*G
- So a-a' = (b'-b)*d (mod N)

The pairs (a,b) and (a+d, b-1) give the same output!
This periodicity in the input-output relationship is what QFT detects.

### The Eigenvalue View

Consider the eigenstates of the "multiply by G" operator U_G:
- U_G|P> = |P + G>
- Eigenstates: |u_s> = (1/sqrt(N)) * SUM_{k=0}^{N-1} exp(-2*pi*i*s*k/N) * |k*G>
- Eigenvalues: exp(2*pi*i*s/N)

If we prepare |Q> = |d*G>, it decomposes into eigenstates, and phase estimation
extracts the eigenvalue phases, revealing d.

---

## What Our 4-bit Simulation Actually Does

### Honest Assessment

Our simulation is NOT true quantum computing. Here's what really happens:

**Classical Enumeration Disguised:**
```python
# Step 2 "Oracle" - this is just classical brute force!
for d in range(1, N):
    if scalar_multiply(d, G) == target_point:
        marked_d = d  # Found it classically!
```

**Fake QFT:**
```python
# Our QFT doesn't detect periodicity - it just does DFT on a
# boolean "did we find it" array, which is meaningless
amplitudes[d] = 1.0 if d*G == target else 0.0  # Already know the answer!
```

**Disconnected Measurement:**
The "measured value" (e.g., 0x02) has no mathematical connection to the
answer (e.g., 0x07). The post-processing just brute-forces until it works.

### What a Real Quantum Simulation Would Need

1. **True Superposition:** Maintain all 2^n amplitudes without collapsing
2. **Unitary Evolution:** Apply gates that preserve quantum properties
3. **Real QFT:** Apply the actual transform on the amplitude vector
4. **Probabilistic Measurement:** Sample from probability distribution
5. **Repeat Until Success:** Shor's needs O(1) repetitions on average

### Why 4 Bits is Educational But Not Quantum

With only 19 possible values, classical brute force is instant.
The "quantum advantage" only matters at scale:
- 4-bit: Classical = 19 ops, Quantum = 64 ops (worse!)
- 256-bit: Classical = 2^128 ops (impossible), Quantum = 256^3 ops (feasible)

---

## The Actual QFT Circuit

For n qubits, QFT uses these gates:

```
|q_0> ---H---R_2---R_3---...---R_n---SWAP---
|q_1> -------o-----R_2---...---R_{n-1}------
|q_2> -------------o-----...---R_{n-2}------
 ...
|q_{n-1}>--------------------o--------------

Where:
- H = Hadamard gate: H = (1/sqrt(2)) * [[1,1],[1,-1]]
- R_k = Phase rotation: R_k = [[1,0],[0,exp(2*pi*i/2^k)]]
```

Gate count: O(n^2) = O((log N)^2)

For 256-bit ECDSA:
- n = 256 qubits (minimum, more for workspace)
- ~65,536 gates for QFT alone
- Plus controlled point additions (~256^3 operations)

---

## Timeline for Breaking Bitcoin

| Milestone | Estimate | Requirement |
|-----------|----------|-------------|
| Current state (2024) | Now | ~1000 noisy qubits |
| Error-corrected logical qubit | 2025-2027 | ~1000 physical per logical |
| 100 logical qubits | 2028-2030 | ~100,000 physical qubits |
| Break 256-bit ECDSA | 2035-2040? | ~2000-4000 logical qubits |

The timeline is uncertain because:
1. Error correction overhead may decrease with better qubits
2. Algorithmic improvements may reduce qubit requirements
3. Manufacturing breakthroughs are unpredictable

---

## Post-Quantum Cryptography

Algorithms believed to be resistant to quantum attacks:

1. **Lattice-based:** CRYSTALS-Kyber, CRYSTALS-Dilithium (NIST standard)
2. **Hash-based:** SPHINCS+, XMSS (signatures only)
3. **Code-based:** Classic McEliece
4. **Isogeny-based:** SIKE (broken in 2022!), CSIDH

Bitcoin will eventually need to migrate to post-quantum signatures.
Some proposals include Lamport signatures or lattice-based schemes.

---

## References

1. Shor, P.W. (1994). "Algorithms for quantum computation"
2. Proos & Zalka (2003). "Shor's discrete logarithm quantum algorithm for elliptic curves"
3. Roetteler et al. (2017). "Quantum resource estimates for computing elliptic curve discrete logarithms"
4. NIST Post-Quantum Cryptography Standardization (2024)
