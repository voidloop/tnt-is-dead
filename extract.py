from tabulate import tabulate
import click
import csv
import re

CSV_FILE = 'dump_release_tntvillage_2019-08-30.csv'


def size_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def tnt_data(human_readable, title_filter):
    regexp = None
    if title_filter:
        regexp = re.compile(title_filter)

    with open(CSV_FILE, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if regexp and not regexp.search(row['TITOLO']):
                continue

            if human_readable:
                size = size_fmt(int(row['DIMENSIONE']))
            else:
                size = int(row['DIMENSIONE'])

            magnet_link = 'magnet:?xt=urn:btih:{}'.format(row['HASH'])
            yield size, magnet_link, row['TITOLO'].strip()


@click.command()
@click.option('--human-readable', '-h', is_flag=True)
@click.option('--title-filter', '-t', default=None)
def extract(human_readable, title_filter):

    data = tnt_data(human_readable, title_filter)

    colalign = None
    if human_readable:
        colalign = ('right',)

    output = tabulate(data, tablefmt='tsv', colalign=colalign)
    print(output)


if __name__ == '__main__':
    extract()
