from starline.packets import EnginePacket
from starline.wire_pack import PACKED_SIZE, pack_from_wire, pack_perceptual, unpack_perceptual, wire_from_packed


def test_roundtrip_perceptual():
    raw = pack_perceptual(
        v=88.0,
        smoothness=0.91,
        coherence=0.82,
        phase=1.2,
        sync_R=0.65,
        flow_code=2,
        topology_code=3,
    )
    assert len(raw) == PACKED_SIZE
    p = unpack_perceptual(raw)
    assert abs(p["coherence"] - 0.82) < 0.02
    assert abs(p["smoothness"] - 0.91) < 0.02
    assert abs(p["v"] - 88.0) < 2.0


def test_wire_roundtrip():
    wire = [0.5, 0.01, 0.02, 0.9, 0.001, 1, 95, 0, 0, 100, 0.85, 0, 0.7, 2.0, 0, 0.6, 0.5, 2, 0, 1]
    packed = pack_from_wire(wire)
    back = wire_from_packed(packed, wire)
    assert abs(back[10] - wire[10]) < 0.02
    assert abs(back[3] - wire[3]) < 0.02
