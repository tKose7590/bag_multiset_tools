import unittest

from bag_multiset_tools import Bag


class TestBagConstruction(unittest.TestCase):
    def test_empty_constructor(self):
        b = Bag()
        self.assertEqual(len(b), 0)
        self.assertEqual(list(b), [])

    def test_from_list(self):
        b = Bag(["a", "b", "a"])
        self.assertEqual(b.count("a"), 2)
        self.assertEqual(b.count("b"), 1)
        self.assertEqual(len(b), 3)

    def test_from_dict(self):
        b = Bag({"x": 3, "y": 1})
        self.assertEqual(b.count("x"), 3)
        self.assertEqual(b.count("y"), 1)
        self.assertEqual(len(b), 4)

    def test_from_dict_with_zero_count(self):
        b = Bag({"x": 3, "y": 0})
        self.assertEqual(b.count("x"), 3)
        self.assertEqual(b.count("y"), 0)
        self.assertEqual(len(b), 3)

    def test_from_dict_with_negative_count_raises(self):
        with self.assertRaises(ValueError):
            Bag({"x": -1})

    def test_from_dict_with_float_integer_count(self):
        b = Bag({"x": 3.0})
        self.assertEqual(b.count("x"), 3)
        self.assertIsInstance(b.count("x"), int)

    def test_from_dict_with_non_integer_float_raises(self):
        with self.assertRaises(TypeError):
            Bag({"x": 3.5})

    def test_from_dict_with_bool_count_raises(self):
        with self.assertRaises(TypeError):
            Bag({"x": True})

    def test_from_bag(self):
        original = Bag({"a": 2, "b": 1})
        copy = Bag(original)
        self.assertEqual(copy.count("a"), 2)
        self.assertEqual(copy.count("b"), 1)
        copy.remove("a", 1)
        self.assertEqual(original.count("a"), 2)


class TestInsert(unittest.TestCase):
    def test_insert_default_one(self):
        b = Bag()
        b.insert("a")
        self.assertEqual(b.count("a"), 1)

    def test_insert_multiple(self):
        b = Bag()
        b.insert("a", 3)
        self.assertEqual(b.count("a"), 3)
        self.assertEqual(len(b), 3)

    def test_insert_accumulates(self):
        b = Bag()
        b.insert("a", 2)
        b.insert("a", 3)
        self.assertEqual(b.count("a"), 5)

    def test_insert_zero_is_noop(self):
        b = Bag()
        b.insert("a", 0)
        self.assertEqual(b.count("a"), 0)
        self.assertEqual(len(b), 0)

    def test_insert_negative_raises(self):
        b = Bag()
        with self.assertRaises(ValueError):
            b.insert("a", -1)

    def test_insert_bool_raises(self):
        b = Bag()
        with self.assertRaises(TypeError):
            b.insert("a", True)

    def test_insert_float_integer_count(self):
        b = Bag()
        b.insert("a", 2.0)
        self.assertEqual(b.count("a"), 2)
        self.assertIsInstance(b.count("a"), int)


class TestRemove(unittest.TestCase):
    def test_remove_default_one(self):
        b = Bag({"a": 3})
        b.remove("a")
        self.assertEqual(b.count("a"), 2)

    def test_remove_all(self):
        b = Bag({"a": 3})
        b.remove("a", 3)
        self.assertEqual(b.count("a"), 0)
        self.assertNotIn("a", b)

    def test_remove_more_than_present(self):
        b = Bag({"a": 2})
        b.remove("a", 5)
        self.assertEqual(b.count("a"), 0)
        self.assertNotIn("a", b)

    def test_remove_absent_element(self):
        b = Bag({"a": 1})
        b.remove("z", 3)
        self.assertEqual(b.count("z"), 0)
        self.assertEqual(b.count("a"), 1)

    def test_remove_zero_is_noop(self):
        b = Bag({"a": 2})
        b.remove("a", 0)
        self.assertEqual(b.count("a"), 2)

    def test_remove_negative_raises(self):
        b = Bag({"a": 2})
        with self.assertRaises(ValueError):
            b.remove("a", -1)

    def test_remove_bool_raises(self):
        b = Bag({"a": 2})
        with self.assertRaises(TypeError):
            b.remove("a", True)


class TestContainsAndCount(unittest.TestCase):
    def test_contains_present(self):
        b = Bag({"a": 2})
        self.assertIn("a", b)

    def test_contains_absent(self):
        b = Bag({"a": 2})
        self.assertNotIn("z", b)

    def test_count_absent_is_zero(self):
        b = Bag({"a": 2})
        self.assertEqual(b.count("z"), 0)

    def test_count_returns_int(self):
        b = Bag({"a": 2.0})
        self.assertIsInstance(b.count("a"), int)


class TestIteration(unittest.TestCase):
    def test_iter_yields_each_copy(self):
        b = Bag({"a": 2, "b": 1})
        result = sorted(b)
        self.assertEqual(result, ["a", "a", "b"])

    def test_iter_empty_bag(self):
        b = Bag()
        self.assertEqual(list(b), [])


class TestElements(unittest.TestCase):
    def test_elements_returns_pairs(self):
        b = Bag({"a": 2, "b": 1})
        pairs = sorted(b.elements())
        self.assertEqual(pairs, [("a", 2), ("b", 1)])

    def test_elements_snapshot_is_independent(self):
        b = Bag({"a": 2})
        snapshot = b.elements()
        b.insert("a", 1)
        self.assertEqual(snapshot, [("a", 2)])


class TestEquality(unittest.TestCase):
    def test_equal_bags(self):
        a = Bag({"x": 2, "y": 1})
        b = Bag({"x": 2, "y": 1})
        self.assertEqual(a, b)

    def test_unequal_bags_different_counts(self):
        a = Bag({"x": 2})
        b = Bag({"x": 3})
        self.assertNotEqual(a, b)

    def test_unequal_bags_different_elements(self):
        a = Bag({"x": 2})
        b = Bag({"y": 2})
        self.assertNotEqual(a, b)

    def test_equality_with_non_bag(self):
        a = Bag({"x": 2})
        self.assertNotEqual(a, {"x": 2})


class TestClear(unittest.TestCase):
    def test_clear_empties_bag(self):
        b = Bag({"a": 3, "b": 1})
        b.clear()
        self.assertEqual(len(b), 0)
        self.assertEqual(b.count("a"), 0)
        self.assertEqual(list(b), [])


class TestRepr(unittest.TestCase):
    def test_repr_round_trips(self):
        b = Bag({"a": 2, "b": 1})
        r = repr(b)
        restored = eval(r)
        self.assertEqual(restored, b)


class TestFloatKeys(unittest.TestCase):
    def test_float_key_tracking(self):
        b = Bag()
        b.insert(1.5, 2)
        self.assertEqual(b.count(1.5), 2)
        b.remove(1.5, 1)
        self.assertEqual(b.count(1.5), 1)


if __name__ == "__main__":
    unittest.main()
