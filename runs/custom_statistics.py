from filter_utils import make_filter_by_name, make_filter_by_memory_type, make_composite_filter
from processor import PostProcessor, MemoryType, parse_memory_type
from processor_utils import print_bytes


def collect_custom_statistics(processor: PostProcessor):
    request_parts_separator = ','
    memory_types_for_usage = [x.name.lower() for x in
                              (MemoryType.VirtualAlloc, MemoryType.XMemAlloc, MemoryType.KernelPool)]

    print('You should enter a request to collect memory statistics.')
    print(f'Request should content all of following parts, separated by \'{request_parts_separator}\':')
    print(f'1) one of available memory type: {memory_types_for_usage}')
    print(f'2) symbol regex (e.g. \'tcmalloc*\', \'MagnusServerDll*\'')
    print('Press Ctrl+Z to exit...')

    while True:
        try:
            request = input('> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            raw_memory_type, raw_symbol_regex, *_ = request.split(request_parts_separator)
        except ValueError:
            print('Cannot parse request! Seems like separator is missing...')
            continue

        memory_type = parse_memory_type((raw_memory_type or '').strip())
        if memory_type is MemoryType.Unknown:
            print('Cannot parse memory type!')
            continue

        symbol_regex = (raw_symbol_regex or '').strip()
        if len(symbol_regex) == 0:
            print('Symbol regex is empty!')
            continue

        try:
            f1 = make_filter_by_name(symbol_regex)
            f2 = make_filter_by_memory_type(memory_type)
            f = make_composite_filter([f1, f2])
        except ValueError as e:
            print('Failed to prepare filter: ' + str(e))
            continue

        try:
            sum_bytes = processor.sum_bytes_by_custom_filter(f)
            print_bytes(sum_bytes)
        except Exception as e:
            print('Failed to collect statistics! Internal error: ' + str(e))
