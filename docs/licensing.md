# Licensing Rationale

TREMORMESH is dual-licensed, and that's deliberate.

| What | License | Why |
|------|---------|-----|
| **Code & firmware** (`4_*`, `5_*`, `6_*`, `7_*`) | **MIT** | Maximum reuse, zero friction. Drop the detector or consensus engine into any project, commercial or not. |
| **Hardware & docs** (`1_*`, `2_*`, `3_*`, `8_Utils`) | **CERN-OHL-P v2** | Purpose-built for open hardware. It defines "Product", "Documentation", and "Source" precisely - concepts that software licenses don't model well. |

## Why not just MIT everything?

MIT is a *software* license. Applying it to schematics and mechanical drawings
leaves real questions unanswered: what counts as the "source" of a physical
product? What obligations attach to someone who manufactures and sells units?
The CERN Open Hardware Licence family was written by hardware people to answer
exactly those questions, and CERN-OHL-P is the permissive variant - it imposes
no copyleft, matching MIT's spirit while using the right vocabulary for atoms
instead of bits.

## What this means for you

- **Build and sell nodes?** Allowed. Keep the license notices.
- **Fork the detector into your app?** Allowed under MIT.
- **No warranty.** This is a community/research project, not a certified
  life-safety product. See the disclaimers in both licenses.

Full texts: [`LICENSE`](../LICENSE) (CERN-OHL-P) and [`LICENSE-MIT`](../LICENSE-MIT).
