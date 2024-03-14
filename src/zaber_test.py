
class TestAxis:
    def __init__(self):
        pass

    def get_position(self) -> float:
        return 10.

    def move_absolute(self, *args, **kwargs):
        return

def init_zaber() -> tuple:
    return (TestAxis(), TestAxis())

if __name__ == "__main__":
    pass
