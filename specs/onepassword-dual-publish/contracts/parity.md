# Secret Parity Contract

- Read legacy and generated Secret JSON with kubectl into captured memory.
- Require generated `OnePasswordItem Ready=True` before comparison.
- Compare Secret type, exact decoded key set, and each decoded byte string using constant-time comparison.
- Success output: one pair-level PASS line and final `17/17` count.
- Failure output: namespace/pair plus mismatch class/count only; never key names, base64, decoded bytes, or captured kubectl output.
