# Bit-Level Math Operations in ECDSA

This document explains the mathematical operations used in ECDSA at the bit level,
focusing on why certain operations destroy bit relationships and what "reversibility" means.

---

## Operations Summary

| Operation | Time | Space | Math Reversible? | Bit-Traceable? |
|-----------|------|-------|------------------|----------------|
| mod_inverse(a, p) | O(log p) | O(1) | Yes | No |
| point_add(P, Q) | O(log p) | O(1) | Yes* | No |
| scalar_multiply(d, G) | O(log d) | O(1) | No (ECDLP) | No |

*Point subtraction requires knowing both points

---

## 1. Modular Inverse

### The Algorithm: Extended Euclidean Algorithm (EEA)

```python
def mod_inverse(a, p):
    """Find x where a * x = 1 (mod p)"""
    old_r, r = a % p, p
    old_s, s = 1, 0

    while r != 0:
        quotient = old_r // r          # INTEGER DIVISION
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    return old_s % p
```

### Example: mod_inverse(3, 17)

```
Initial: old_r=3, r=17, old_s=1, s=0

Iteration 1:
  quotient = 3 // 17 = 0
  old_r, r = 17, 3 - 0*17 = 17, 3    (swap)
  old_s, s = 0, 1 - 0*0 = 0, 1      (swap)

Iteration 2:
  quotient = 17 // 3 = 5
  old_r, r = 3, 17 - 5*3 = 3, 2
  old_s, s = 1, 0 - 5*1 = 1, -5

Iteration 3:
  quotient = 3 // 2 = 1
  old_r, r = 2, 3 - 1*2 = 2, 1
  old_s, s = -5, 1 - 1*(-5) = -5, 6

Iteration 4:
  quotient = 2 // 1 = 2
  old_r, r = 1, 2 - 2*1 = 1, 0      (r=0, stop)
  old_s, s = 6, -5 - 2*6 = 6, -17

Result: old_s % 17 = 6
Verify: 3 * 6 = 18 = 1 (mod 17) [correct]
```

### Why Division Destroys Bit Relationships

The key operation is **integer division**: `quotient = old_r // r`

**Problem:** Integer division has no simple bit-level pattern.

```
Example: 17 // 3 = 5

  17 in binary: 10001
   3 in binary: 00011
   5 in binary: 00101

There is NO bit-by-bit operation that transforms 10001 and 00011 into 00101.
Division requires comparing magnitudes and repeated subtraction.
```

**Each iteration compounds the problem:**
- Iteration 1: quotient depends on ALL bits of old_r and r
- Iteration 2: new values depend on previous quotient (ALL previous bits)
- Iteration N: result depends on ENTIRE sequence of quotients

**This is called "bit diffusion"** - each output bit depends on all input bits.

### Mathematical vs Bit-Level Reversibility

| Type | Question | Answer |
|------|----------|--------|
| Mathematical | Given y = a^(-1) mod p, find a | Easy: a = y^(-1) mod p |
| Bit-level | Given output bits, trace which input bits affected each | Impossible without full recomputation |

**Mathematical reversibility:** The inverse function is its own inverse.
```
(a^(-1))^(-1) = a (mod p)
```
Both directions cost O(log p). No "hard" direction.

**Bit-level traceability:** Given only the output, you CANNOT determine:
- How many iterations the EEA took
- What the quotients were at each step
- Which input bits "caused" which output bits

---

## 2. The Slope Calculation in Point Addition

Inside `point_add(P, Q)`:

```python
numerator = (Q.y - P.y) % p
denominator = (Q.x - P.x) % p
slope = (numerator * mod_inverse(denominator, p)) % p
```

### The Chain of Destruction

```
Step 1: denominator = (Q.x - P.x) % p
        - Subtraction: bit diffusion via borrow propagation
        - Modulo: wrapping destroys magnitude information

Step 2: inv = mod_inverse(denominator, p)
        - Division sequence destroys all bit patterns
        - Result depends on ENTIRE GCD reduction

Step 3: slope = (numerator * inv) % p
        - Multiplication: each output bit = XOR of many input bit products
        - Modulo: more wrapping
```

**Result:** The slope bits have NO recoverable relationship to P or Q bits.

### Why This Matters for ECDLP

If we're trying to reverse `Q = d * G`:

```
Given: Q = (x_Q, y_Q), G = (x_G, y_G)
Want: d

The path from d to Q:
  d -> [binary representation] -> [sequence of double/add] -> Q

Each double/add involves:
  - Subtraction (bit diffusion)
  - mod_inverse (total bit destruction)
  - Multiplication (more diffusion)
  - Modulo (wrapping)
```

Even if you could somehow "reverse" one point operation, you'd need to know:
1. Was this a double or an add?
2. If add, what was the other point?
3. What intermediate point did we have before this step?

This is circular - answering these requires knowing d!

---

## 3. Complexity Analysis

### Forward Operations

| Operation | Time | Why |
|-----------|------|-----|
| a % p | O(1)* | Single division |
| a * b % p | O(1)* | Multiply + divide |
| mod_inverse(a, p) | O(log p) | ~log(p) iterations of EEA |
| point_add(P, Q) | O(log p) | One mod_inverse dominates |
| scalar_multiply(d, G) | O(log d) | ~log(d) point operations |

*O(1) for fixed-size integers; O(n^2) for arbitrary precision

### Reverse Operations

| Operation | Time | Why |
|-----------|------|-----|
| (a^(-1))^(-1) | O(log p) | Same as forward |
| point_subtract(R, Q) | O(log p) | Need to know Q |
| ECDLP: find d from Q=dG | O(sqrt(N)) best classical | Must search/collide |

---

## 4. What "Reversing Mod Inverse" Would Mean

### Scenario A: You have the output, want the input
```
Given: y = mod_inverse(a, p) = 6
Given: p = 17
Find: a

Solution: a = mod_inverse(6, 17) = 3
Time: O(log p)
```
This is EASY. Just apply the inverse again.

### Scenario B: You have intermediate computation state
```
Given: At some step in scalar_multiply, the slope was s = 0x1234...
Find: What were the points P, Q such that s = (Q.y - P.y) / (Q.x - P.x)?

This is UNDERDETERMINED:
  - One equation: s * (Q.x - P.x) = (Q.y - P.y) (mod p)
  - Four unknowns: P.x, P.y, Q.x, Q.y
  - Plus constraint: both points on curve
  - Still infinite solutions!
```

### Scenario C: You want to trace bit-by-bit
```
Given: mod_inverse(a, p) = y
Question: Which bit of 'a' most affected bit 3 of 'y'?

Answer: ALL of them, roughly equally.
The EEA mixes everything together through the quotient sequence.
There is no "bit 3 of a maps to bit 7 of y" relationship.
```

---

## 5. Implications for Cryptanalysis

### What DOESN'T Work

1. **Bit-by-bit analysis:** No correlation between input/output bits
2. **Partial information:** Knowing some output bits doesn't help find input bits
3. **Reverse tracing:** Can't work backward through scalar_multiply without knowing d

### What DOES Work

1. **Algebraic attacks:** If you know the nonce k, direct formula gives d
2. **Side channels:** Timing/power analysis might leak the bit pattern of d directly
3. **Weak parameters:** Small groups, smooth order enable shortcuts
4. **Quantum:** Shor's algorithm bypasses the bit-level entirely

### The Security Assumption

ECDSA security does NOT rely on mod_inverse being "hard to reverse."

It relies on ECDLP: given Q and G, finding d where Q = d*G requires O(sqrt(N)) work.

The bit destruction from mod_inverse is a SYMPTOM of why this is hard, not the CAUSE.
The cause is that scalar multiplication loses information about d's binary representation
through the combination of many operations.

---

## References

- Menezes, van Oorschot, Vanstone. "Handbook of Applied Cryptography" Ch. 14
- Knuth. "The Art of Computer Programming" Vol. 2, Section 4.5.2 (GCD algorithms)
- Hankerson, Menezes, Vanstone. "Guide to Elliptic Curve Cryptography" Ch. 3
