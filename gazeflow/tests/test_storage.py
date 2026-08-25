from gazeflow.config import Settings
from gazeflow.storage.profiles import ProfileStore

def test_profile_round_trip(tmp_path):
    path = tmp_path / "profiles.json"; store = ProfileStore(path); settings = Settings(dwell_seconds=2.0); store.save(settings, "demo")
    assert store.load("demo").dwell_seconds == 2.0
