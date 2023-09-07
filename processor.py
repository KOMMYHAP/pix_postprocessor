from enum import Enum
from typing import Callable


class FilterPass(Enum):
    ShouldContinue = 1,
    ShouldAbort = 2,
    ShouldConsume = 3


class MemoryType(Enum):
    VirtualAlloc = 1,
    XMemAlloc = 2,
    KernelPool = 3,
    Unknown = 42


def parse_memory_type(raw_memory_type: str) -> MemoryType:
    raw_memory_type_lower = raw_memory_type.lower()
    for memory_type in MemoryType:
        if memory_type.name.lower() == raw_memory_type_lower:
            return memory_type
    return MemoryType.Unknown


class Node:
    def __init__(self):
        self.size = 0
        self.name = '<no name>'
        self.memory_type = MemoryType.Unknown
        self.children = []
        self.parent = None

    def set_data(self, size: int, name: str, memory_type: MemoryType):
        self.size = size
        self.name = name
        self.memory_type = memory_type


NodeFilter = Callable[[Node], FilterPass]


class PostProcessor:
    def __init__(self, pix_data_file):
        self._data_file = pix_data_file
        self._prepare_environment()

        self._separator = '\t'
        self._indent_separator = '    '
        root = self._create_model()
        self._root = root

    def sum_bytes_by_custom_filter(self, filter_callback: NodeFilter) -> int:
        sum_bytes = 0

        # self._root is fake node, so we should iterate by its children
        for node in self._root.children:
            sum_bytes += self._collect_bytes_rec(node, filter_callback)
        return sum_bytes

    def _collect_bytes_rec(self, node: Node, filter_callback: NodeFilter) -> int:
        filter_pass = filter_callback(node)
        if filter_pass == FilterPass.ShouldAbort:
            return 0
        if filter_pass == FilterPass.ShouldConsume:
            return node.size

        sum_bytes = 0
        for child in node.children:
            sum_bytes += self._collect_bytes_rec(child, filter_callback)

        return sum_bytes

    def _prepare_environment(self):
        if not self._data_file.exists() or not self._data_file.is_file():
            raise ValueError('File with pix data is invalid: ' + str(self._data_file))

    def _create_model(self) -> Node:

        with self._data_file.open('r') as f:
            headers = f.readline()
            header_size, header_name, *_ = headers.split(self._separator)
            unit_multiplier = self.parse_unit_multiplier(header_size)

            root = Node()
            root.set_data(0, '<internal root>', MemoryType.Unknown)
            active_node = root
            indent_level = 0

            while True:
                raw_data = f.readline()
                if len(raw_data) == 0:
                    break

                raw_size, raw_name, raw_memory_type, *_ = raw_data.split(self._separator)

                # 1. Parse current indent
                next_indent_level = raw_name.count(self._indent_separator) + 1

                # 2. Go to parent scope, if previous one completed
                level_count_to_parent = (indent_level - next_indent_level) + 1
                while level_count_to_parent > 0:
                    level_count_to_parent -= 1
                    active_node = active_node.parent

                # 3. Add child to active scope, if indent was not changed
                child = self.add_child(active_node, Node())
                indent_level = next_indent_level

                # 4. Parse node's data
                size_bytes = int(float(raw_size.replace(',', '')) * unit_multiplier)
                memory_type = parse_memory_type(raw_memory_type)
                name = raw_name[(indent_level - 1) * len(self._indent_separator):]
                child.set_data(size_bytes, name, memory_type)

                # 5. Change active scope to child's one
                active_node = child

        return root

    @staticmethod
    def add_child(root: Node, child: Node) -> Node:
        root.children.append(child)
        child.parent = root
        return child

    @staticmethod
    def parse_unit_multiplier(raw_size: str) -> int:
        start_offset = raw_size.index('(') + 1
        end_offset = raw_size.index(')')
        unit = raw_size[start_offset:end_offset]

        # PIX use 2^10 base for Kilo-, Mega-, Giga- prefixes
        if unit == 'B':
            return 1
        elif unit == 'KB':
            return 1024
        elif unit == 'MB':
            return 1024 * 1024
        elif unit == 'GB':
            return 1024 * 1024 * 1024

        raise ValueError('Invalid unit: ' + unit)
