class Resource:
    """ Object. Is to be assigned to subject.
    """

    def __init__(self, _id):
        self._id = _id

    def __repr__(self) -> str:
        return f'R{str(self._id)}'
