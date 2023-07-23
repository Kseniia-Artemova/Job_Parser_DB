from configparser import ConfigParser


def config(path_to_file, section="postgresql"):
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


def accept_command(commands):
    while True:
        command = input("\nКоманда: ").lower().strip()
        if command not in commands:
            print("Такая команда не существует. Попробуйте ещё раз.")
            continue

        return command


def run_command(commands, command):
    commands[command][1]()