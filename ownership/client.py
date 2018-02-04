class Client:
    """Subject. Claims objects.

    Attributes:
        _id: int

        claimed: [Resource]

        priority: int Is set to PRIORITY_NORMAL by default
    """

    PRIORITY_LOW = 0
    PRIORITY_NORMAL = 1

    def __init__(self, _id):
        self._id = _id
        self.priority = self.PRIORITY_NORMAL
        self.claimed = []

    def __repr__(self) -> str:
        return f'S{self._id}'
