import os

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_test_parser(filename, parser_class):
    return parser_class(get_test_xml(filename))


def get_test_xml(filename):
    data_file = os.path.join(TEST_DATA_DIR, filename)
    with open(data_file) as h:
        return h.read()