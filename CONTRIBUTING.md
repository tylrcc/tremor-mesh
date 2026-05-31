# Contributing

Thanks for even looking. This only becomes useful if a lot of people build and poke at it, so anything from a typo fix to a new firmware feature is welcome.

## Where help goes furthest

- **Embedded / firmware:** power management, LoRa uplink, OTA updates, three-axis fusion, fixed-point tuning on the ESP32.
- **Seismology / DSP:** better characteristic functions, magnitude estimation, telling a real P-wave from a door slam.
- **Backend / distributed systems:** scaling the gateway, time sync, keeping fake triggers out.
- **Hardware:** a real PCB, a decent enclosure, better sensor coupling.
- **Just building one:** seriously, deploy a node and tell me where it breaks. That's the most useful report I can get right now.

## Getting set up

```bash
git clone https://github.com/tylrcc/tremor-mesh
cd tremor-mesh
pip install -e .
pytest -q
```

`python 5_Algorithms/demo.py` and `python 7_Simulations/network_sim.py` are the quickest way to see things move.

## A few rules

- If you touch the detector, change it in **both** `tremormesh/stalta.py` and `4_Firmware/node/node.ino`, and update the tests. The Python is the source of truth.
- Tests have to pass before I'll merge. CI runs `pytest` on every PR.
- Keep PRs small and say *why*, not just *what*.
- Don't commit generated junk (plots, build output, binaries). It's git-ignored for a reason.

## Issues

Use the issue tracker for bugs and ideas. If you find a way to make the network fire a false alarm or stay quiet when it shouldn't, that's a security thing, flag it (see [SECURITY.md](SECURITY.md)) so it gets looked at first.

By sending a PR you're agreeing your code goes out under MIT and any hardware/docs under CERN-OHL-P, same as the rest of the repo.
