import re
from typing import List

from processor import NodeFilter, Node, FilterPass, MemoryType


def make_filter_by_name(pattern: str) -> NodeFilter:
    try:
        regex = re.compile(pattern, flags=re.RegexFlag.IGNORECASE)
    except (TypeError, KeyError, ValueError, re.error) as e:
        raise ValueError(str(e))

    def filter_by_name(node: Node) -> FilterPass:
        if regex.search(node.name):
            return FilterPass.ShouldConsume
        return FilterPass.ShouldContinue

    return filter_by_name


def make_filter_by_memory_type(memory_type: MemoryType) -> NodeFilter:
    def filter_by_memory_type(node: Node) -> FilterPass:
        if node.memory_type != memory_type:
            return FilterPass.ShouldAbort
        return FilterPass.ShouldContinue

    return filter_by_memory_type


def make_filter_node_and_ban_children_by_name(pattern_in_node: str, pattern_in_child: str) -> NodeFilter:
    node_filter = make_filter_by_name(pattern_in_node)
    child_filter = make_filter_by_name(pattern_in_child)

    def filter_node_without_child_rec(node: Node) -> FilterPass:
        if child_filter(node) == FilterPass.ShouldConsume:
            # node has a prohibited name
            return FilterPass.ShouldAbort
        for child in node.children:
            if filter_node_without_child_rec(child) == FilterPass.ShouldAbort:
                return FilterPass.ShouldAbort
        return FilterPass.ShouldConsume

    def filter_node_and_ban_children(node: Node) -> FilterPass:
        if node_filter(node) == FilterPass.ShouldConsume and \
                filter_node_without_child_rec(node) == FilterPass.ShouldConsume:
            return FilterPass.ShouldConsume

        return FilterPass.ShouldContinue

    return filter_node_and_ban_children


def make_composite_filter(filters: List[NodeFilter]) -> NodeFilter:
    def composite_filter(node: Node) -> FilterPass:
        for f in filters:
            filter_pass = f(node)
            if filter_pass != FilterPass.ShouldContinue:
                return filter_pass
        return FilterPass.ShouldContinue

    return composite_filter


def make_filter_by_name_and_memory_type(pattern: str, memory_type: MemoryType) -> NodeFilter:
    f1 = make_filter_by_name(pattern)
    f2 = make_filter_by_memory_type(memory_type)
    return make_composite_filter([f2, f1])
