from starline.hex_lattice import (
    encode_lattice_hex,
    loop_seal_manifest,
    schrodinger_from_flow,
)


def test_hex_encode():
    h = encode_lattice_hex({"v": 50.0, "c": 0.8, "S": 0.9})
    assert "0x76" in h
    assert "0x63" in h
    assert h["0x76"] == 50.0


def test_schrodinger_normalized():
    s = schrodinger_from_flow("flow", 0.95, 0.05)
    d = s.as_dict()
    n = sum(d[k] ** 2 for k in ("alpha", "beta", "gamma", "delta"))
    assert abs(n - 1.0) < 0.01


def test_loop_sealed():
    m = loop_seal_manifest()
    assert m["sealed"] is True
    assert "0x76" in m["hex_lattice"]
