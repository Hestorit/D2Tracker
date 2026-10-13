from collections.abc import Iterable


class ObjectCollection:


    def __init__(self, items: Iterable = ()):
        self._items = list(items)

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def clear(self):
        self._items.clear()

    def all(self) -> list:
        return self._items.copy()

    def find_by_id(self, object_id, attribute='account_id'):
        for item in self._items:
            if getattr(item, attribute, None) == object_id:
                return item
        return None


    def sort_by(self, key, reverse=False):
        return sorted(self._items, key=lambda item: getattr(item, key), reverse=reverse)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item in self._items

    def __getitem__(self, index):
        return self._items[index]

    def __str__(self):
        return f'ObjectCollection({len(self)} objects)'

    def __repr__(self):
        return f'ObjectCollection(items={self._items!r})'

    def __eq__(self, other):
        if not isinstance(other, ObjectCollection):
            return NotImplemented
        return self._items == other._items
