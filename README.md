# bag_multiset_tools

A small, dependency-free Python library providing a `Bag` (multiset) that tracks per-element multiplicities with `insert`, `remove`, and `count` operations.

## Usage

```python
from bag_multiset_tools import Bag

b = Bag(["apple", "apple", "banana"])
b.insert("apple", 2)
print(b.count("apple"))  # 4

b.remove("apple", 3)
print(b.count("apple"))  # 1
print(len(b))            # 2 (1 apple + 1 banana)

for element in b:
    print(element)
```

## Why

`collections.Counter` in the standard library is close in spirit, but it
mixes mapping semantics with multiset semantics and does not raise on
negative counts at construction time. This library is a deliberately narrow
abstraction: a bag that supports insert, remove, count, length, iteration,
equality, and a snapshot `elements()` view — nothing else. The trade-off is
flexibility for predictability: every ambiguous case has one defined
behaviour.

## Edge cases and decisions

- **Counts are integers.** Passing `3.0` is accepted (it is an unambiguous
  integer); `3.5` raises `TypeError`. Booleans are rejected even though
  `isinstance(True, int)` is `True` in Python, because accepting them
  silently leads to surprises.
- **`remove` never raises for over-removal.** Calling `b.remove("x", 10)`
  when only 2 copies exist removes the element entirely. If you need to
  detect over-removal, check `b.count("x")` first.
- **`insert` and `remove` with count 0 are no-ops**, so callers can pass
  computed counts without extra branches.
- **Negative counts raise `ValueError`** on both `insert` and `remove`, and
  at construction from a dict.
- **Equality compares only the element->multiplicity mapping.** The cached
  total length is never part of the comparison, so staleness cannot break
  equality.
