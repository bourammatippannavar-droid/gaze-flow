from gazeflow.tracking.calibration import Calibration

def test_calibration_maps_identity_points():
    calibration = Calibration()
    for x, y in [(0,0),(1,0),(0.5,0.5),(0,1),(1,1)]: calibration.add(x, y, x, y)
    assert calibration.ready
    mapped = calibration.map(0.25, 0.75)
    assert abs(mapped[0] - 0.25) < 0.01
    assert abs(mapped[1] - 0.75) < 0.01
