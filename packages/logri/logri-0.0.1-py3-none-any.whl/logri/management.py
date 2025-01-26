import argparse
import codecs
import dataclasses
import enum
import os

prog = 'logri'

input_text = argparse.ArgumentParser(add_help=False)
input_text.add_argument(
    '--vf', '--verilog-file', action='extend', nargs='+', default=[],
    metavar='VERILOG_FILE', dest='verilog_file')
input_text.add_argument('-e', '--encoding', default='utf-8')

output_bin = argparse.ArgumentParser(add_help=False)
output_bin.add_argument('-o', '--output', default='logri_out.bin')

input_bin = argparse.ArgumentParser(add_help=False)
input_bin.add_argument(
    '--bf', '--binary-file',
    nargs=1, metavar='BINARY_FILE', dest='binary_file')


@dataclasses.dataclass
class CommandEntry:
    name: str
    help: str
    parents: list[argparse.ArgumentParser]
    _parser: argparse.ArgumentParser | None = None

    @property
    def parser(self) -> argparse.ArgumentParser:
        if self._parser is None:
            self._parser = argparse.ArgumentParser(
                prog=f'{prog} {self.name}',
                parents=self.parents)
        return self._parser


compile_entry = CommandEntry(
    'compile', 'Compile verilog to python object', [input_text, output_bin])

simulate_entry = CommandEntry(
    'simulate', 'Run simulation on compiled object', [input_bin])

command_dict: dict[str, list[argparse.ArgumentParser]] = {
    'compile': compile_entry,
    'simulate': simulate_entry,
    }


def print_general_help():
    print(f'usage: {prog} <command> [options]\n')
    print('commands:')
    command_help_format = '  {: <16}{}\n'
    for command, entry in command_dict.items():
        print(command_help_format.format(command, entry.help), end='')
    print('  help            Show help for commands')


def print_command_help(argv: list[str]) -> None:
    command = argv[0]
    if command in command_dict:
        command_dict[command].parser.print_help()
    elif command == 'help':
        print_general_help()
    else:
        print_general_help()
        print(f'\nerror: unrecognized command: {command}')


def get_arguments(argv):
    if len(argv) < 2:
        print_general_help()
        return None

    if len(argv) == 2:
        print_command_help(argv[1:2])
        return None

    command = argv[1]
    if command in command_dict:
        args = command_dict[command].parser.parse_args(argv[2:])
        args.command = command
        return args
    elif command == 'help':
        print_command_help(argv[2:])
        return None
    else:
        print_general_help()
        print(f'\nerror: unrecognized arguments: {' '.join(argv[1:])}')
        return None


class Action(enum.Enum):
    COMPILE = 'compile'
    SIMULATE = 'simulate'


@dataclasses.dataclass
class TextFileDescription():
    path: str
    encoding: str


class TaskDescription():
    def __init__(self, command: str) -> None:
        self.action: Action = Action(command)
        match self.action:
            case Action.COMPILE:
                self.output: str = ''
                self.verilog: list[TextFileDescription] = []
            case Action.SIMULATE:
                self.binary: list[str] = []

    def __getattr__(self, name):
        raise AttributeError(f'Task with action {self.action} '
                             'do not have attribute {name}.')

    def set_output(self, output: str) -> None:
        match self.action:
            case Action.COMPILE:
                self.check_file_writable(output)
                self.output = output
            case Action.SIMULATE:
                self.__getattr__('output')

    def append_verilog_file(self, file: str, encoding: str) -> None:
        self.check_encoding(encoding)
        self.check_file_readable(file)
        self.verilog.append(TextFileDescription(file, encoding))

    def extend_verilog_files(self, files: list[str], encoding: str) -> None:
        self.check_encoding(encoding)
        for file in files:
            self.check_file_readable(file)
        descriptions = self.text_files_get_descriptions(files, encoding)
        self.verilog.extend(descriptions)

    def append_binary_file(self, file: str) -> None:
        self.check_file_readable(file)
        self.binary.append(file)

    def extend_binary_file(self, files: str) -> None:
        for file in files:
            self.check_file_readable(file)
        self.binary.extend(files)

    def check_file_writable(self, file: str) -> None:
        if os.path.exists(file):
            if os.path.isfile(file):
                if os.access(file, os.W_OK):
                    return
                else:
                    raise PermissionError(f'Have no permission to '
                                          f'write file {repr(file)}.')
            else:
                raise IsADirectoryError(f'{repr(file)} is not a file.')
        else:
            directory = os.path.dirname(os.path.abspath(file))
            if os.path.isdir(directory):
                if os.access(directory, os.W_OK):
                    return
                else:
                    raise PermissionError(f'Have no permission to write in '
                                          f'directory {repr(directory)}.')
            else:
                raise NotADirectoryError(
                    f'{repr(directory)} is not a directory.')

    def check_encoding(self, encoding: str) -> None:
        codecs.lookup(encoding)

    def check_file_readable(self, file: str) -> None:
        if os.path.exists(file):
            if os.path.isfile(file):
                if os.access(file, os.R_OK):
                    return
                else:
                    raise PermissionError(f'Have no permission to '
                                          f'read file {repr(file)}.')
            else:
                raise IsADirectoryError(f'{repr(file)} is not a file.')
        else:
            raise FileNotFoundError(f'Cannot find file {repr(file)}.')

    def text_files_get_descriptions(
            self, files: list[str], encoding: str
            ) -> list[TextFileDescription]:
        return [TextFileDescription(file, encoding) for file in files]


def arguments_to_task_description(args) -> TaskDescription:
    match args.command:
        case 'compile':
            task = TaskDescription(args.command)
            task.set_output(args.output)
            task.extend_verilog_files(args.verilog_file, args.encoding)
            return task
        case 'simulate':
            task = TaskDescription(args.command)
            task.extend_binary_file(args.binary_file)
            return task
        case _:
            raise ValueError(f'Cannot parse command {repr(args.command)}')


def execute_task(task: TaskDescription):
    print('Cannot execute any task now.')
    print('Do nothing and exit')
