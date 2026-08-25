from gazeflow.tracking.cursor_mapping import apply_sensitivity, map_fingertip, remap_active_region


def test_active_region_reaches_edges():
    assert remap_active_region(0.15, 0.85, 0.15) == (0.0, 1.0)


def test_sensitivity_scales_around_center():
    x, y = apply_sensitivity(0.4, 0.6, 2.0)
    assert abs(x - 0.3) < 1e-9
    assert abs(y - 0.7) < 1e-9


def test_mapping_clamps_output():
    x, y = map_fingertip(0.0, 1.0, margin=0.15, gain=2.0)
    assert (x, y) == (0.0, 1.0)
