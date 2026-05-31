# What this is and why

## The problem

Earthquake early warning isn't science fiction. Japan and Mexico have had it for years, and the US west coast has ShakeAlert now. When it works it gives people anywhere from a few seconds to most of a minute before the shaking hits, which is enough to do something useful.

The catch is cost. These systems run on research-grade seismometers that run into the thousands of dollars each, so the networks are sparse and expensive to grow. Most of the seismically active world has nothing.

## The bet

Cheap MEMS accelerometers have gotten good. Not seismometer-good, but good enough to catch the onset of an earthquake if you're not too far away. So instead of a handful of perfect, expensive stations, what if you put out thousands of $15 ones?

Any single cheap node is noisy and you can't trust it. That's fine, you're not supposed to. A real quake trips every node in an area at almost the same moment, while a truck or a slammed door trips exactly one. If you only believe an event when a bunch of separated nodes agree within a couple of seconds, the noise mostly cancels out and the earthquakes stand out. Density does the work that an expensive sensor would otherwise have to.

## How a warning actually happens

1. A quake sends out a fast, weak P-wave and a slower, much more destructive S-wave.
2. Each node runs an STA/LTA trigger and usually catches the P-wave within a second.
3. Triggers go to a gateway, which only declares an event when enough geographically-separated nodes agree in a short window.
4. The alert goes out before the S-wave arrives. Right by the epicenter that lead time is basically zero; farther out it grows.

## What's in here

The whole reference design, end to end:

- ESP32 + MEMS node firmware (`4_Firmware/`)
- the detector, as readable tested Python that the firmware mirrors (`tremormesh/`, tests in `5_Algorithms/`)
- the consensus logic and an MQTT gateway (`tremormesh/consensus.py`, `6_Server/`)
- hardware BOM, wiring, enclosure notes (`3_Hardware/`)
- a simulation that runs the entire pipeline with no hardware at all (`7_Simulations/`)

## What it isn't

It's a research and learning project, not something certified to keep you alive. Don't lean on it as your only warning. Single nodes are noisy, coverage and mounting quality matter more than anything, and the hard parts (clock sync across nodes, stopping someone from injecting fake triggers, estimating how strong the shaking will be) are still open. Those are written up in [the roadmap](../docs/roadmap.md).
