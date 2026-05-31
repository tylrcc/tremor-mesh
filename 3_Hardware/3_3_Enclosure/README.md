# Enclosure

The enclosure has one job that matters: **couple the accelerometer rigidly to
the building.** Everything else is weather protection.

## Design guidance

- **Rigid mount, not rubber feet.** Vibration isolation is the enemy here - you
  *want* to transmit ground motion to the sensor. Use a flat base that bolts or
  epoxies to a slab, foundation, or load-bearing wall.
- **Keep the sensor close to the mounting plane.** Long standoffs add resonances.
- **Leave a cable strain relief.** A tug on the USB cable shouldn't move the board.

## Files

Drop your printable models here:

- `node_base.stl` / `node_lid.stl` - print in PLA (indoor) or ASA/PETG (outdoor).
- `node_enclosure.step` - editable CAD source (preferred for contributions).

> Large binaries bloat clones over time - prefer attaching released models to a
> GitHub Release and keeping the editable CAD source here.
