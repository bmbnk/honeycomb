import unittest

from hive.engine import hive as h


class TestHiveAdd(unittest.TestCase):
    def setUp(self):
        self.hive = h.Hive()

    def test_if_added(self):
        piece_to_move = {}
        piece_to_move["bG1"] = "bG1"
        piece_to_move["wA1"] = "wA1 -bG1"
        piece_to_move["wA2"] = "wA2 \\bG1"
        piece_to_move["wA3"] = "wA3 bG1/"
        piece_to_move["wG1"] = "wG1 bG1-"
        piece_to_move["wG2"] = "wG2 bG1\\"
        piece_to_move["wG3"] = "wG3 /bG1"

        for piece, move in piece_to_move.items():
            self.hive.add(move)

            with self.subTest(piece=piece):
                self.assertTrue(self.hive.is_in_hive(piece))
                self.assertFalse(self.hive.is_position_empty(move))

    def test_add_next_to_not_existing_piece(self):
        move_str = "wG1 bQ/"

        with self.assertRaises(h.InvalidPositionError):
            self.hive.add(move_str)

    def test_add_existing_piece(self):
        first_piece = "wA1"
        second_piece = "bA1"

        self.hive.add(first_piece)
        self.hive.add(f"{second_piece} -{first_piece}")

        with self.assertRaises(h.PieceAlreadyExistsError):
            self.hive.add(f"{first_piece} -{second_piece}")


class TestHiveRemove(unittest.TestCase):
    def setUp(self):
        self.hive = h.Hive()

    def test_remove_not_existing_piece(self):
        with self.assertRaises(h.PieceNotExistsError):
            self.hive.remove("wA1")

    def test_if_removed(self):
        first_piece = "wA1"
        piece = "bG1"
        move_str = f"{piece} {first_piece}/"

        self.hive.add(first_piece)
        self.hive.add(move_str)
        self.hive.remove(piece)

        self.assertTrue(self.hive.is_position_empty(move_str))
        self.assertFalse(self.hive.is_in_hive(piece))


class TestHiveIsPositionEmpty(unittest.TestCase):
    def setUp(self):
        self.hive = h.Hive()

    def test_when_empty(self):
        first_piece = "bG1"
        second_piece = "wA1"

        self.hive.add(first_piece)
        self.hive.add(f"{second_piece} -{first_piece}")

        self.assertTrue(self.hive.is_position_empty(f"wA2 {first_piece}-"))

    def test_when_invalid_position(self):
        move_str = "wG1 bQ/"

        with self.assertRaises(h.InvalidPositionError):
            self.hive.is_position_empty(move_str)

    def test_when_not_empty(self):
        piece_to_position = {}
        piece_to_position["bG1"] = "bG1"
        piece_to_position["wA1"] = "-bG1"

        for piece, position in piece_to_position.items():
            move_str = f"{piece} {position}"
            self.hive.add(move_str)

            with self.subTest(position=position):
                self.assertFalse(self.hive.is_position_empty(move_str))


class TestHiveIsInHive(unittest.TestCase):
    def setUp(self):
        self.hive = h.Hive()

    def test_when_not_in_hive(self):
        piece_str = "wB1"

        self.assertFalse(self.hive.is_in_hive(piece_str))

    def test_when_in_hive(self):
        piece_to_move = {}
        piece_to_move["bG1"] = "bG1"
        piece_to_move["wA1"] = "wA1 -bG1"

        for piece, move in piece_to_move.items():
            self.hive.add(move)

            with self.subTest(piece=piece):
                self.assertTrue(self.hive.is_in_hive(piece))


if __name__ == "__main__":
    unittest.main()
