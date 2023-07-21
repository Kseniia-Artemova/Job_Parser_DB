from configparser import ConfigParser
import os


def config(path_to_file="database_config.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(path_to_file)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, path_to_file))
    return db