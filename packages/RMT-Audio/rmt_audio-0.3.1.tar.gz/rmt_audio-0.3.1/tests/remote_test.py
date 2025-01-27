from rmt_audio.remote import remote

def test_first():
    v = remote(1,2,3)
    assert v is not None
