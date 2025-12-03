# Rollback System

Educational tools for reversing cryptographic operations, focusing on ECDSA discrete logarithm attacks.

## Algorithm Comparison

### ECDLP Attacks (Reversing Scalar Multiplication)

| Algorithm | Time | Space | Best When | File |
|-----------|------|-------|-----------|------|
| Brute Force | O(n) | O(1) | Never | `bruteECDSA4bitMechanism.py` |
| Baby-step Giant-step | O(sqrt(n)) | O(sqrt(n)) | General case | `bruteECDSA4bitMechanism.py` |
| Pollard's Rho | O(sqrt(n)) | O(1) | Memory constrained | `bruteECDSA4bitMechanism.py` |
| Pollard's Kangaroo | O(sqrt(W)) | O(1) | Key in bounded range [a,b], W=b-a | `kangarooECDSA4bitMechanism.py` |
| Pohlig-Hellman | O(sum of e_i * sqrt(p_i)) | varies | Smooth group order | `pohligHellmanECDSA4bitMechanism.py` |
| Lookup Table | O(1) | O(n) | Small n, repeated queries | `bruteECDSA4bitMechanism.py` |
| Nonce Recovery | O(1) | O(1) | Known/weak nonce | `bruteECDSA4bitMechanism.py` |
| Shor (quantum) | O(n^3) | - | Quantum computer exists | `shorECDSA4bitMechanism.py` |

### Supporting Operations (Forward Direction)

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Modular Inverse | O(log p) | O(1) | Extended Euclidean Algorithm |
| Point Addition | O(log p) | O(1) | One mod_inverse per add |
| Scalar Multiply | O(log d) | O(1) | Double-and-add, ~log(d) point ops |
| Signature (sign) | O(log N) | O(1) | One scalar mult + arithmetic |
| Verification | O(log N) | O(1) | Two scalar mults + one add |

### Scalar Multiply Reversal Complexity

**Notation:**
- N = bit length of key (256 for secp256k1)
- p = field prime (~2^N)
- H = Hamming weight of k (number of 1-bits, avg N/2)

**Forward `scalar_multiply(k, G)`:**

| Operation | Count | Cost each | Total |
|-----------|-------|-----------|-------|
| point_add to result | H (~N/2) | O(N) | O(H * N) |
| point_double | N-1 | O(N) | O(N * N) |
| **Total forward** | | | **O(N^2)** |

**Reverse by undoing point_adds:**

| What you'd need | Complexity | Why |
|-----------------|------------|-----|
| Guess bit pattern | 2^N possibilities | Don't know which bits are 1 |
| Verify each guess | O(N^2) | Run forward, compare to Q |
| **Total brute reverse** | **O(2^N * N^2)** | |

**Best classical (Pollard rho):**

| Step | Complexity |
|------|------------|
| Collision search | O(sqrt(2^N)) = O(2^(N/2)) |
| Per operation | O(N^2) |
| **Total** | **O(2^(N/2) * N^2)** |

**Real time for N=256:**

| Method | Operations | Time @ 10^12 ops/sec |
|--------|-----------|---------------------|
| Forward | ~65,000 | microseconds |
| Brute reverse | 2^256 * 65k | 10^65 years |
| Pollard rho | 2^128 * 65k | 10^26 years |
| Shor (quantum) | poly(N^3) | minutes (with ~4000 qubits) |

**Key insight:** The mod_inverse inside each point_add is O(N) and mathematically reversible. The bottleneck is **not knowing which of the 2^N bit patterns to reverse**.

### Why Reversing Scalar Multiply Doesn't Help Mod Inverse

**Q: Can ECDLP reversal help compute modular inverse?**

**A: No.** They are fundamentally different problems:

1. **mod_inverse is already efficient** - O(log p) via Extended Euclidean Algorithm
2. **ECDLP finds the scalar d**, not intermediate computation states
3. The mod_inverse calls inside point_add are "consumed" - you can't recover them from Q

**The core issue:** Inside `scalar_multiply(d, G)`:
```
Step 1: point_add uses mod_inverse(denom_1, P) -> slope_1
Step 2: point_add uses mod_inverse(denom_2, P) -> slope_2
...
Final: Q = d * G
```

Given only Q and G, you cannot determine:
- How many point additions occurred (depends on binary representation of d)
- What the intermediate points were
- What denominators were inverted
- What slopes were computed

**To "reverse" mod_inverse you'd need:** The intermediate points, but finding them requires knowing d, which is the ECDLP itself!

**Mod inverse is self-reversing:** If y = a^(-1) mod p, then a = y^(-1) mod p. Both directions cost O(log p). There's no hard direction.

**See [../reference/classical_ecdlp_algorithms.md](../reference/classical_ecdlp_algorithms.md) for detailed algorithm explanations.**

## Key Insights

1. **Kangaroo** - Optimal when key is bounded to range of width W. If you leak 128 bits of a 256-bit key, search drops from O(2^128) to O(2^64) - potentially attackable!

2. **Pohlig-Hellman** - Exploits smooth group order. Bitcoin's secp256k1 has prime order N, so PH provides no speedup. But if N=2^32, PH solves in ~64 ops instead of 2^16 for BSGS.

3. **The Classical-Quantum Gap** - Best classical is O(sqrt(n)) = O(2^128) for Bitcoin. Shor is O(n^3) = O(256^3). That's ~10^30x difference. Nothing classical bridges this gap - it requires quantum parallelism.

4. **Bitcoin's Security** - secp256k1 group order is a 256-bit prime. Pohlig-Hellman useless. Only sqrt(n) attacks apply, requiring 2^128 operations (infeasible).

## Partial Key Knowledge (Kangaroo)

| Bits Unknown | Search Space | Kangaroo Steps | Feasibility |
|--------------|--------------|----------------|-------------|
| 256 | 2^256 | 2^128 | 10^26 years @ 10^12 ops/sec |
| 128 | 2^128 | 2^64 | Years with massive compute |
| 64 | 2^64 | 2^32 | Hours to days |
| 32 | 2^32 | 2^16 = 65K | Milliseconds |
| 6 | 2^6 | 2^3 = 8 | Instant |

You need to know ~190+ bits before Kangaroo becomes practical.

## 4-Bit ECDSA (Educational)

The 4-bit ECDSA module is fully functional - all attacks actually work. Perfect for learning.

```
Curve: y^2 = x^3 + 2x + 2 (mod 17)
Generator: G = (0x05, 0x01)
Order: N = 19 (prime - resistant to Pohlig-Hellman)
Private keys: 0x01 to 0x12
```

### Quick Start

```python
from rollback.rollbackECDSA4bit import RollbackECDSA4bit
from cryptography.ecdsa4bit import generate_keypair, to_hex

# Create and break a keypair
private_key, public_key = generate_keypair(0x07)
rollback = RollbackECDSA4bit(public_key, attack_type='baby_step_giant_step')
result = rollback.run()
print(f"Recovered: {to_hex(result['private_key'])}")  # 0x07
```

### Compare All Attacks

```python
from rollback.rollbackECDSA4bit import RollbackECDSA4bit
from cryptography.ecdsa4bit import generate_keypair

_, public_key = generate_keypair(0x0A)
RollbackECDSA4bit.compare_attacks(public_key)
```

### Run Demos

```bash
python rollback/bruteECDSA4bitMechanism.py      # Classical attacks
python rollback/kangarooECDSA4bitMechanism.py   # Bounded range search
python rollback/pohligHellmanECDSA4bitMechanism.py  # Smooth order attack
python rollback/shorECDSA4bitMechanism.py       # Quantum simulation
```

## CLI Usage

```bash
# 4-bit ECDSA (working)
python rollback/run.py key1 --type ecdsa4bit

# Compare attack methods
python rollback/run.py --compare

# Limit iterations
python rollback/run.py key3 --max-iterations 5000

# Ctrl+C anytime to stop gracefully and print stats
```

## RIPEMD-160 Rollback

Experimental reverse-engineering of RIPEMD-160 hash function.

```python
from rollback import RollbackRipeMD160

rollback = RollbackRipeMD160(address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
result = rollback.run()
```

## Configuration

All config in `config.py`:
- `RollbackConfig.RUNNER_CONFIG` - Runner settings
- `RollbackConfig.RIPEMD160_CONFIG` - RIPEMD-160 settings
- `RollbackConfig.ECDSA_CONFIG` - ECDSA settings
- `RollbackConfig.TEST_ADDRESSES` - Test data

## Extending

```python
from rollback.rollbackMechanism import RollbackMechanism

class MyMechanism(RollbackMechanism):
    def run(self):
        # Your attack logic
        self.result = {'found': True, 'private_key': d}
        return self.result
```

## Notes

- Educational/research code only
- 4-bit ECDSA is fully working
- 256-bit attacks are computationally infeasible (by design)
- See main CLAUDE.md for research context
