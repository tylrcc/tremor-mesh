# FAQ

### Can I rely on this to warn me about earthquakes?

No, not yet, and I'd rather say that loudly than bury it. It's alpha and it's a research/hobby project. Treat it as something to learn from and build on, not as a replacement for an official warning service.

### How is this different from ShakeAlert or MyShake?

They're great and I'm not trying to replace them. The difference is the angle:

- MyShake uses phones. A phone in your pocket couples to your leg, not the ground. These nodes get bolted to a structure, which picks up real motion far better.
- ShakeAlert uses a small number of expensive, excellent instruments. This bets the other way: lots of cheap ones, leaning on density instead of per-sensor quality.
- All of this is open: hardware, firmware, and the data. You can build one, read every line, and change it.

The point isn't to beat national systems. It's to put *some* warning in places that currently have none.

### Can a $2 accelerometer really detect earthquakes?

For early warning, yes, with caveats. You're catching the onset of the P-wave, not producing clean research waveforms. One cheap node is noisy, which is exactly why the system only trusts events that several nodes agree on. If you want closer to research quality, the Pro build uses an ADXL355.

### What stops a prankster from triggering a fake city-wide alert?

Right now, not enough, and I'm not going to pretend otherwise. Consensus already requires several separated nodes to agree, plus a cooldown, so one fake node isn't enough. Signing triggers per-node so the gateway can reject spoofed ones is the planned fix, and I treat alert integrity as a [security issue](../SECURITY.md).

### How much warning do you actually get?

Depends how far you are from the epicenter. Right on top of it you're in the blind zone and get nothing. Farther out you get seconds to tens of seconds. Run `python 7_Simulations/network_sim.py` and it'll show you the trade-off with real numbers.

### Do I need hardware to try it?

Nope. `pip install -e .`, then `tremormesh-demo` and `tremormesh-sim`. Or run the scripts in `5_Algorithms/` and `7_Simulations/` directly.

### What's the license?

Hardware and docs are CERN-OHL-P, code and firmware are MIT. Long version in [licensing.md](licensing.md).

### How do I help?

Build a node and tell me what's confusing, grab a `good first issue`, or bring seismology / embedded / distributed-systems chops. Start at [CONTRIBUTING.md](../CONTRIBUTING.md).
