from pathlib import Path

from processor import PostProcessor
from runs.custom_statistics import collect_custom_statistics

if __name__ == '__main__':
    print('Processing PIX data may take a few minutes...')

    working_directory = Path(r'C:\Path\To\Your\Directory')
    pix_data_file = working_directory / 'pix.data'
    processor = PostProcessor(pix_data_file)

    collect_custom_statistics(processor)

    print('Have a good day! Bye-bye.')
