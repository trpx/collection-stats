import abc
import itertools
import math
import collections
from .utils import Compact
try:
    import numpy as np
    std_func = np.std
except ImportError:
    import statistics
    std_func = statistics.pstdev


class _NoName:
    pass


class CollectionStatsCollector:
    """
    Usage:

    collector = CollectionStatsCollector()

    for collection in some_collections:
        uid = ...  # optional - see below
        collector.add(collection, uid=uid)  # uid is optional (used for include_samples=True)

    print(collector.count)
    print(collector)
    print(collector.format(include_samples=True))
    """

    def __init__(self):
        self._stats = None

    def add(self, collection, uid=None):
        stats = collection_stats(collection, uid=uid)
        if self._stats is not None:
            self._stats += stats
        else:
            self._stats = stats

    @property
    def count(self):
        return self._stats.count

    def format(self, include_samples=True):
        return self._stats.format(include_samples=include_samples)

    def __str__(self):
        return str(self._stats)


def collection_stats(node, uid=None, _name=_NoName):
    args, kwargs = (node, ), dict(name=_name, uid=uid)
    if isinstance(node, (dict, )):
        return MappingNodeStats(*args, **kwargs)
    elif isinstance(node, (list, set, tuple, )):
        return IterableNodeStats(*args, **kwargs)
    else:
        return PrimitiveNodeStats(*args, **kwargs)


class CollectionStats(metaclass=abc.ABCMeta):
    MAX_SAMPLES = 5
    MAX_RUN_SIZES = 1000
    MAX_SIZES = 10

    def __init__(self, node, name=_NoName, uid=None):
        self._node = node
        self._name = name
        self._type_name = type(node).__name__
        self._uid = uid

        self._count = 1
        self._min = self._size
        self._avg = self._size
        self._max = self._size
        self._std = 0

        self._size_counter = collections.Counter()
        if self._size is not None:
            self._size_counter[self._size] = 1

        self._type_samples = set()
        self._min_samples = {}
        self._max_samples = {}
        self._populate_samples()

        self._children_nodes = {}
        self._populate_children_nodes()

    @property
    def count(self):
        return self._count

    def samples(self):
        samples = set()
        samples |= self._type_samples | set(self._min_samples.keys()) | set(self._max_samples.keys())
        for i in self._descendant_nodes():
            samples |= i.samples()
        return samples

    def _descendant_nodes(self):
        nodes = set()
        for k, node in self._children_nodes.items():
            nodes.add(node)
            nodes.update(node._descendant_nodes())
        return nodes

    def _populate_samples(self):
        if self._uid is not None:
            self._type_samples = {self._uid, }
            if self._size is not None:
                self._min_samples = {self._uid: self._size}
                self._max_samples = {self._uid: self._size}

    @abc.abstractmethod
    def _populate_children_nodes(self): pass

    def _add_child_node(self, node, name=_NoName):
        child_node = collection_stats(
            node, uid=self._uid, _name=name,
        )
        key = (type(node), name)
        if key not in self._children_nodes:
            self._children_nodes[key] = child_node
        else:
            self._children_nodes[key] += child_node

    @property
    def _size(self):
        if isinstance(self._node, (int, float)):
            return self._node
        elif isinstance(self._node, (dict, list, set, str)):
            return len(self._node)
        else:
            return None

    def __str__(self):
        return self._as_str()

    def format(self, include_samples=True, include_sizes=True):
        return self._as_str(include_samples=include_samples, include_sizes=include_sizes)

    def _as_str(self, indentation='', last_child=False, include_samples=True, include_sizes=True):
        """1 dict avg3.0 min3 max3 std0 type[1] min[1] max[1]"""
        mapping_value_overindent = 2
        own_str_parts = list()
        if last_child:
            postfix = '└ '
        else:
            postfix = '├ '
        if indentation and self._name is _NoName:
            count_indentation = indentation[:-2] + postfix
        elif self._name is _NoName:
            count_indentation = indentation
        else:
            indentation += ' ' * mapping_value_overindent
            count_indentation = indentation
        own_str_parts.append(f'{count_indentation}{self._count} {self._type_name}')
        if self._size is not None:
            mn = self._min if not isinstance(self._min, bool) else int(self._min)
            mx = self._max if not isinstance(self._max, bool) else int(self._max)
            str_part = f'avg {Compact.float(self._avg)} '
            if mn != mx:
                str_part += f'({mn}–{mx}) '
            str_part += f'std {Compact.float(self._std)}'
            own_str_parts.append(str_part)
        if self._size_counter and include_sizes:
            str_part = ''
            if len(self._size_counter) > self.MAX_RUN_SIZES:
                str_part += 'sample'
            elif len(self._size_counter) > self.MAX_SIZES:
                str_part += f'top{self.MAX_SIZES}freq'
            else:
                str_part += 'all'
            sizes = dict(self._size_counter.most_common(self.MAX_SIZES))
            str_part += f'{sizes}'
            own_str_parts.append(str_part)
        if self._type_samples and include_samples:
            own_str_parts.append('uids:')
            own_str_parts.append(f'type{sorted(self._type_samples)}')
            if self._size is not None:
                own_str_parts.append(f'min{sorted(self._min_samples)} max{sorted(self._max_samples)}')
        parts = [' '.join(own_str_parts), ]
        if self._name is not _NoName:
            name = str(self._name).replace('OrderedDict', 'dict').replace('NoneType', 'None')
            parts.insert(0, f'{indentation[:-2-mapping_value_overindent]+postfix}{repr(name)}:')
        children_nodes = self._sorted_children_nodes
        children_count = len(children_nodes)
        children_str_parts = []
        for i, node in enumerate(children_nodes):
            if i+1 < children_count:
                child_indentation = indentation + '  │ '
            else:
                child_indentation = indentation + '    '
            children_str_parts.append(
                node._as_str(
                    indentation=child_indentation,
                    last_child=i+1 == children_count,
                    include_samples=include_samples
                )
            )
        return '\n'.join(itertools.chain(parts, children_str_parts))

    @property
    def _sorted_children_nodes(self):
        return sorted(
            self._children_nodes.values(),
            key=lambda x: (
                x.priority,
                x._size is None,
                x._size if x._size is not None else -1,
                x._name if x._name is not _NoName else '',
            )
        )

    def __add__(self, other):
        if type(self._node) is not type(other._node):
            raise NotImplementedError()
        if self._size is not None:
            self._add_samples(other)
            self._min = min(self._min, other._min)
            self._max = max(self._max, other._max)
            self._avg = (self._avg * self._count + other._avg * other._count) / (self._count + other._count)
            if len(self._size_counter) <= self.MAX_RUN_SIZES:
                self._size_counter.update(other._size_counter)
                if len(self._size_counter) > self.MAX_RUN_SIZES:
                    self._size_counter = collections.Counter(
                        dict(self._size_counter.most_common(self.MAX_RUN_SIZES+1)))

            # std
            if self._count > 1 and other._count == 1:
                self._std = self._std_with_added_size(other._size)
            elif other._count > 1 and self._count == 1:
                self._std = other._std_with_added_size(self._size)
            elif self._count > 1 and other._count > 1:
                self._std = math.sqrt((self._std ** 2 + other._std ** 2) / 2)
            else:
                self._std = std_func([self._size, other._size])

        self._count += other._count
        for k, v in other._children_nodes.items():
            if k in self._children_nodes:
                self._children_nodes[k] += v
            else:
                self._children_nodes[k] = v
        return self

    def _std_with_added_size(self, size):
        n = self._count + 1
        std = self._std
        avg = self._avg
        return ((n - 2) / (n - 1) * std ** 2 + (size - avg) ** 2 / n) ** 0.5

    def _add_samples(self, other):
        max_sample_count = self.MAX_SAMPLES
        if len(self._type_samples) < max_sample_count:
            self._type_samples |= other._type_samples
            if len(self._type_samples) > max_sample_count:
                self._type_samples = set(sorted(self._type_samples)[:max_sample_count])
        self._min_samples.update(other._min_samples)
        self._max_samples.update(other._max_samples)
        self._min_samples = self._trim_samples(self._min_samples.items())
        self._max_samples = self._trim_samples(self._max_samples.items(), right=False)

    def _trim_samples(self, samples_items, right=True):
        if len(samples_items) > self.MAX_SAMPLES:
            samples_items = sorted(
                samples_items,
                key=lambda x: x[1]
            )
            if right:
                samples_items = samples_items[:self.MAX_SAMPLES]
            else:
                samples_items = samples_items[-self.MAX_SAMPLES:]
        return dict(samples_items)


class MappingNodeStats(CollectionStats):
    priority = 3

    def _populate_children_nodes(self):
        for k, v in self._node.items():
            self._add_child_node(v, name=k)


class IterableNodeStats(CollectionStats):
    priority = 2

    def _populate_children_nodes(self):
        for i in self._node:
            self._add_child_node(i)


class PrimitiveNodeStats(CollectionStats):
    priority = 1

    def _populate_children_nodes(self):
        pass
