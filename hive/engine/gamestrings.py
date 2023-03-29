class MoveStringsDecoder:
    _relation_signs = frozenset({"/", "-", "\\"})

    @property
    @classmethod
    def relation_signs(cls) -> frozenset:
        return cls._relation_signs

    @classmethod
    def get_piece_to_move(cls, move_str: str) -> str:
        return move_str.split()[0]

    @classmethod
    def _get_position_str(cls, move_str: str) -> str:
        str_parts = move_str.split()

        if len(str_parts) == 1:
            return move_str
        return str_parts[1]

    @classmethod
    def get_ref_piece(cls, move_str: str) -> str:
        pos_str = cls._get_position_str(move_str)
        if pos_str == move_str and any(sign in pos_str for sign in cls._relation_signs):
            return ""
        return pos_str.strip("".join(cls._relation_signs))
