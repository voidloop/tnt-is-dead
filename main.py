import logging
import os
import sqlite3
from datetime import datetime

from tabulate import tabulate
import click
import csv
from pathlib import Path

DB_FILE = str(Path.home().joinpath('.tntisdead.db'))


def size_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def create_schema(conn):
    create_table_sql = """
    CREATE TABLE magnets (
        data TIMESTAMP,
        hash VARCHAR(255), 
        topic NUMBER,
        post NUMBER,
        autore VARCHAR(255),
        titolo VARCHAR(255), 
        descrizione VARCHAR(255),
        dimensione NUMBER,
        categoria NUMBER 
    );
    """
    c = conn.cursor()
    c.execute(create_table_sql)
    conn.commit()


def db_file_option(exists=True):
    def wrapper(fn):
        return click.option('--db', 'db_file', help='The database file.',
                            show_default=True,
                            type=click.Path(exists=exists, dir_okay=False),
                            default=DB_FILE)(fn)
    return wrapper


@click.group()
@click.option('--debug', '-d', help='Print debug messages.', is_flag=True)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


def format_link(hash_):
    return 'magnet:?xt=urn:btih:{}'.format(hash_)


@cli.command()
@db_file_option(exists=True)
@click.option('--ignore-case', '-i', help='Ignore case distinctions.', is_flag=True)
@click.option('--human-readable', '-h', help='Show a human readable table.', is_flag=True)
@click.option('--link-only', '-l', help='Print only the magnet links.', is_flag=True)
@click.option('--glob', '-g', help='Use PATTERN as a glob pattern.', is_flag=True)
@click.argument('keyword')
@click.pass_context
def search(ctx, db_file, ignore_case, human_readable, link_only, glob, keyword):
    """
    Search releases in TNT Village's dump.
    """
    if not os.path.exists(db_file):
        raise click.UsageError('{} does not exist, please use "import" command to create it.'.format(DB_FILE))

    logging.debug('Building SQL query...')
    select_sql = """SELECT dimensione, hash, titolo, descrizione FROM magnets WHERE """

    if glob:
        operator = 'GLOB'
    else:
        operator = 'LIKE'
        keyword = "%" + keyword + "%"

    if ignore_case:
        select_sql += """LOWER(descrizione) {0} LOWER(?) OR LOWER(titolo) {0} LOWER(?)""".format(operator)
    else:
        select_sql += """descrizione {0} ? OR titolo {0} ?""".format(operator)

    select_sql += """ ORDER BY titolo;"""

    logging.debug(select_sql)

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(select_sql, [keyword] * 2)

    logging.debug('Fetching data...')
    data = [(row[0], format_link(row[1]), *row[2:]) for row in c.fetchall()]

    try:
        if data:
            if link_only:
                for row in data:
                    click.echo(row[1])
            else:
                colalign = None
                if human_readable:
                    data = [(size_fmt(row[0]), *row[1:]) for row in data]
                    colalign = ('right',)

                output = tabulate(data, tablefmt='plain', colalign=colalign,
                                  headers=('SIZE', 'LINK', 'TITLE', 'DESCRIPTION'))
                click.echo(output)
        else:
            logging.debug('Releases not found.')
            ctx.exit(1)
    finally:
        logging.debug('Closing database...')
        conn.close()


def import_data(conn, file):
    insert_sql = """INSERT INTO magnets VALUES (?,?,?,?,?,?,?,?,?);"""
    c = conn.cursor()
    with open(file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        for row in csv_reader:
            c.execute(insert_sql, (
                datetime.fromisoformat(row['DATA']),
                row['HASH'].strip(),
                int(row['TOPIC']),
                int(row['POST']),
                row['AUTORE'].strip(),
                row['TITOLO'].strip(),
                row['DESCRIZIONE'].strip(),
                int(row['DIMENSIONE']),
                int(row['CATEGORIA'])
            ))
    conn.commit()


def count_magnets(conn):
    select_sql = """SELECT COUNT(*) FROM magnets;"""
    c = conn.cursor()
    c.execute(select_sql)
    return c.fetchone()[0]


@cli.command(name='import')
@db_file_option(exists=False)
@click.option('--force', '-f', help='If the database file already exists, remove it.', is_flag=True)
@click.argument('dump_file', metavar='DUMP', type=click.Path(exists=True))
def import_(db_file, force, dump_file):
    """
    Import TNT Village dump file.
    """
    if os.path.exists(db_file):
        if not force:
            if not click.confirm('{} already exists, do you want overwrite it?'):
                return
        logging.debug('Removing "{}"...'.format(db_file))
        os.unlink(db_file)

    logging.debug('Connecting to "{}"...'.format(db_file))
    conn = sqlite3.connect(db_file)
    create_schema(conn)
    click.echo('Importing releases...')
    import_data(conn, dump_file)
    click.echo('Imported {} releases.'.format(count_magnets(conn)))
    conn.close()


if __name__ == '__main__':
    cli()
