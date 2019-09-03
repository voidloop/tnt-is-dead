import csv
from tabulate import tabulate
import click


CSV_FILE = 'dump_release_tntvillage_2019-08-30.csv'


def size_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def tnt_data(human_readable):
    with open(CSV_FILE, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if human_readable:
                size = size_fmt(int(row['DIMENSIONE']))
            else:
                size = int(row['DIMENSIONE'])

            yield (size, row['HASH'], row['TITOLO'])


@click.command()
@click.option('--human-readable', '-h', is_flag=True)
def extract(human_readable):

    data = tnt_data(human_readable)
    if human_readable:
        output = tabulate(data, tablefmt='tsv', colalign=('right',))
    else:
        output = tabulate(data, tablefmt='tsv')
    print(output)


if __name__ == '__main__':
    extract()
