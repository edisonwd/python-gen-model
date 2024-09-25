import sys
from getpass import getpass
from optparse import OptionParser

from .enum.enum import ModelType
from .python_gen_model import print_models, err, config


def get_option_parser():
    parser = OptionParser(usage='usage: %prog [options] database_name')
    ao = parser.add_option
    ao('-H', '--host', dest='host')
    ao('-p', '--port', dest='port', type='int')
    ao('-u', '--user', dest='user')
    ao('-P', '--password', dest='password', action='store_true')
    ao('-o', '--orm', dest='orm', choices=[e.value for e in ModelType],
       help=f'Choose an ORM to generate code , support: {[e.value for e in ModelType]}. default: sqlmodel',
       default='sqlmodel')
    ao('-t', '--tables', dest='tables',
       help=('Only generate the specified tables. Multiple table names should '
             'be separated by commas.'))
    return parser


def main():
    parser = get_option_parser()
    options, args = parser.parse_args()

    if len(args) < 1:
        err('Missing required parameter "database"')
        parser.print_help()
        sys.exit(1)

    database = args[-1]
    config['database'] = database
    if options.host:
        config['host'] = options.host
    if options.port:
        config['port'] = options.port
    if options.user:
        config['user'] = options.user
    if options.password:
        config['password'] = getpass()

    if not options.tables:
        err('Missing required parameter "tables"')
        return
    else:
        tables = [table.strip() for table in options.tables.split(',')
                  if table.strip()]

    print_models(tables, config, options.orm)


if __name__ == '__main__':
    main()
