"""Bag (multiset) implementation with integer multiplicities.

A bag is an unordered collection where each element has an associated
non-negative integer multiplicity. This module deliberately fixes a few
ambiguous decisions up front, so that callers know exactly what to expect:

* Multiplicities are integers. Floating-point keys are allowed (they are
  hashable), but counts are always ``int``.
* ``insert`` and ``remove`` raise ``ValueError`` on negative counts rather
  than silently clamping — catching bugs early is worth a tiny bit of extra
  ceremony.
* ``remove`` with a count larger than the current multiplicity removes the
  element entirely; it does not raise. This mirrors the intuition of
  "take as many as you can, up to n". If you need an error on over-removal,
  call ``count`` first.
* Equality between bags considers only the current mapping; the cached
  ``__len__`` value is never part of the comparison so staleness cannot
  break equality.
"""

from __future__ import annotations


class Bag:
    """An unordered multiset tracking per-element multiplicities.

    Backed by a plain dict so there are no third-party dependencies and no
    import-time cost beyond a single class definition. A cached total count
    avoids an ``O(n)`` iteration on every ``len()`` call, which matters when
    bags are used in hot paths.
    """

    __slots__ = ("_counts", "_total")

    def __init__(self, iterable=None):
        self._counts = {}
        self._total = 0
        if iterable is None:
            return
        if isinstance(iterable, Bag):
            self._counts = dict(iterable._counts)
            self._total = iterable._total
            return
        if isinstance(iterable, dict):
            for element, count in iterable.items():
                count = self._validate_count(count)
                if count < 0:
                    raise ValueError(
                        "negative count %r for element %r" % (count, element)
                    )
                if count == 0:
                    continue
                self._counts[element] = count
                self._total += count
            return
        for element in iterable:
            self._counts[element] = self._counts.get(element, 0) + 1
            self._total += 1

    @staticmethod
    def _validate_count(count):
        """Coerce ``count`` to ``int`` and require it be integral and non-negative.

        ``True``/``False`` are ints in Python (``True == 1``). We reject them
        explicitly so that ``Bag({'x': True})`` is a TypeError, not a silent
        quirk. ``3.0`` is accepted because it is an unambiguous integer value;
        ``3.5`` is rejected.
        """
        if isinstance(count, bool):
            raise TypeError("count must be an int, not bool")
        if not isinstance(count, int):
            if isinstance(count, float) and count.is_integer():
                count = int(count)
            else:
                raise TypeError("count must be an int")
        return count

    def insert(self, element, count=1):
        """Add ``count`` copies of ``element``.

        ``count`` must be a non-negative integer. A count of zero is a no-op
        so callers can pass through computed values without an extra branch.
        """
        if count == 0:
            return
        count = self._validate_count(count)
        if count < 0:
            raise ValueError("count must be non-negative, got %d" % count)
        self._counts[element] = self._counts.get(element, 0) + count
        self._total += count

    def remove(self, element, count=1):
        """Remove up to ``count`` copies of ``element``.

        If ``element`` is absent, this is a no-op. If ``count`` exceeds the
        current multiplicity, the element is removed entirely and no error
        is raised. To detect over-removal, compare ``count`` with
        ``self.count(element)`` beforehand.
        """
        count = self._validate_count(count)
        if count < 0:
            raise ValueError("count must be non-negative, got %d" % count)
        if count == 0:
            return
        current = self._counts.get(element, 0)
        if current == 0:
            return
        new_count = current - count
        if new_count <= 0:
            del self._counts[element]
            self._total -= current
        else:
            self._counts[element] = new_count
            self._total -= count

    def count(self, element):
        """Return the multiplicity of ``element`` (zero if absent)."""
        return self._counts.get(element, 0)

    def __contains__(self, element):
        return self._counts.get(element, 0) > 0

    def __len__(self):
        """Total number of stored elements (sum of multiplicities)."""
        return self._total

    def __iter__(self):
        """Yield each element repeated by its multiplicity.

        The iteration order matches the underlying dict insertion order, which
        in CPython 3.7+ is the order elements were first inserted. Callers
        that need a stable order regardless of insertion history should sort
        the output themselves.
        """
        for element, multiplicity in self._counts.items():
            for _ in range(multiplicity):
                yield element

    def elements(self):
        """Return a list of (element, multiplicity) pairs.

        A snapshot view: mutating the bag afterwards does not affect the
        returned list. We return a list rather than a view object so callers
        can iterate, slice, or index without worrying about invalidation.
        """
        return list(self._counts.items())

    def clear(self):
        """Remove all elements and reset the cached total."""
        self._counts.clear()
        self._total = 0

    def __eq__(self, other):
        """Bags are equal iff their element->multiplicity mappings are equal.

        Only compares ``_counts``, never the cached ``_total``, so a stale
        total can never cause two bags with identical mappings to compare
        unequal.
        """
        if isinstance(other, Bag):
            return self._counts == other._counts
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self):
        return "Bag(%r)" % (dict(self._counts),)
