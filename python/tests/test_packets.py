"""Packet encoding — round-trip wire, layer separation."""

import numpy as np

from starline import CoherentMotionEngine, SplineTrack
from starline.engine import ControlInput
from starline.flow import FlowState
from starline.packets import (
    WIRE_SIZE,
    EnginePacket,
    TrackLattice,
    decode_perceptual,
    encode_packet,
)
from starline.topology import TopologyClass, analyze_track_topology


def test_wire_round_trip():
    eng = CoherentMotionEngine(track=SplineTrack.oval())
    eng.add_player(0)
    eng.set_control(0, ControlInput(throttle=0.6))
    snap = eng.step(1 / 60)[0]
    p = eng.players[0]
    pkt = encode_packet(
        p,
        eng.track.length,
        0.01,
        0.02,
        snap.sync_R,
        snap.resonance,
        snap.input_noise,
        topology=TopologyClass.SUSTAIN,
        flow_state=FlowState(snap.flow_state),
    )
    wire = pkt.to_wire()
    assert len(wire) == WIRE_SIZE
    back = EnginePacket.from_wire(wire)
    assert abs(back.chemical.coherence - pkt.chemical.coherence) < 1e-9
    assert back.geometric.smoothness == pkt.geometric.smoothness


def test_track_lattice_sample():
    tr = SplineTrack.oval()
    segs = analyze_track_topology(tr, n=64)
    n = 64
    sn = np.linspace(0, 1, n, endpoint=False)
    k = np.array([tr.curvature(float(s * tr.length)) for s in sn])
    tc = np.zeros(n, dtype=np.uint8)
    lat = TrackLattice.from_track(sn, k, tc, name="oval")
    k0, _, code = lat.sample_at(0.5)
    assert isinstance(k0, float)
    assert isinstance(code, int)


def test_decode_perceptual_bounded():
    eng = CoherentMotionEngine(track=SplineTrack.oval())
    eng.add_player(0)
    snap = eng.step(1 / 60)[0]
    p = eng.players[0]
    pkt = encode_packet(
        p, eng.track.length, 0.01, 0.02, snap.sync_R, 0.5, 0.0, flow_state="stable"
    )
    psi = decode_perceptual(pkt)
    assert 0.0 <= psi["dissonance"] <= 2.0
    assert 0.0 <= psi["flow"] <= 1.0
