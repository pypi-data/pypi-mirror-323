import sys

from . import management


def main():
    args = management.get_arguments(sys.argv)
    if args is None:
        exit()

    task = management.arguments_to_task_description(args)
    if task is None:
        print('No task to execute.')
        exit()

    management.execute_task(task)


if __name__ == "__main__":
    main()
