from processor import PostProcessor, NodeFilter


def print_bytes(size_bytes: int):
    print_units = 1024.0
    print(f'{size_bytes} bytes ')
    if size_bytes > 0:
        print(f'{size_bytes / print_units ** 1:.3f} Kib ')
        print(f'{size_bytes / print_units ** 2:.3f} Mib ')
        print(f'{size_bytes / print_units ** 3:.3f} Gib ')


def run_and_print_summary(processor: PostProcessor, title: str, filter: NodeFilter):
    print(f'Allocation summary for \"{title}\"')
    try:
        sum_bytes = processor.sum_bytes_by_custom_filter(filter)
        print_bytes(sum_bytes)
    except Exception as e:
        print('Failed to collect statistics! Internal error: ' + str(e))
    print()
