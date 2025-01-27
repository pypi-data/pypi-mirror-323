from pathlib import Path
import argparse
import os
import pandas as pd


def put(args: argparse.Namespace):
    """
    :param file: filename
    :param tags: tags for link. eg: python:multiprocess:socket
    :param value: value for link
    :return:
    """
    file = args.file
    tags = args.tags
    value = args.value
    home = Path.joinpath(Path.home(), 'savetxt')
    header = ["tags", "value"]
    Path(home).mkdir(exist_ok=True)
    tags_list = tags.split(',')
    filepath = Path.joinpath(home, f'{file}.csv')
    row_to_add = pd.DataFrame(columns=header, data=[[tags_list, value]])
    file_exists = os.path.exists(filepath)
    if file_exists:
        row_to_add.to_csv(filepath, mode='a', header=False, index=False)
    else:
        row_to_add.to_csv(filepath, mode='a', header=True, index=False)


def cat(args: argparse.Namespace):
    file = args.file
    home = Path.joinpath(Path.home(), 'savetxt')
    filepath = Path.joinpath(home, f'{file}.csv')
    if filepath.exists():
        data = pd.read_csv(filepath)
        print(data.to_string())


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    put_parser = subparsers.add_parser('put')
    put_parser.add_argument('file')
    put_parser.add_argument('tags')
    put_parser.add_argument('value')
    put_parser.set_defaults(put_parser=True, func=put)

    cat_parser = subparsers.add_parser('cat')
    cat_parser.add_argument('file')
    cat_parser.set_defaults(cat_parser=True, func=cat)
    args = parser.parse_args()
    if args.func:
        args.func(args)


if __name__ == '__main__':
    main()
