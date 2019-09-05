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


def tnt_data(title_filter):
    regexp = None
    if title_filter:
        regexp = re.compile(title_filter)

    with open(CSV_FILE, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if regexp and not regexp.search(row['TITOLO']):
                continue
            yield int(row['DIMENSIONE']), row['HASH'], row['TITOLO']


def do_sort(data, sort_by):
    if sort_by.lower() == 'title':
        def fun(x):
            return x[2].lower()
    else:
        def fun(x):
            return x[0]
    return sorted(data, key=fun)


@click.command()
@click.option('--human-readable', '-h', is_flag=True)
@click.option('--title-filter', '-t', default=None)
@click.option('--sort-by', '-s', type=click.Choice(['size', 'title']), default='title')
def extract(human_readable, title_filter, sort_by):

    data = []
    for size, btih, title in tnt_data(title_filter):
        magnet_link = 'magnet:?xt=urn:btih:{}'.format(btih)
        data.append([size, magnet_link, title.strip()])

    data = do_sort(data, sort_by)
    if human_readable:
        for row in data:
            row[0] = size_fmt(row[0])

    colalign = None
    if human_readable:
        colalign = ('right',)

    output = tabulate(data, tablefmt='tsv', colalign=colalign)
    print(output)


if __name__ == '__main__':
    extract()
