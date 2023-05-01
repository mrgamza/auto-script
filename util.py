def get_os():
    import platform
    return platform.system()


def get_platform():
    import sys
    return sys.platform


def is_windows():
    return get_platform() == "win32"


def get_call_result(cmd):
    import subprocess
    fd_popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout
    data = fd_popen.read().strip()
    fd_popen.close()
    return data


def call_multiprocess(cmd):
    import subprocess
    from multiprocessing import Process
    Process(target=subprocess.call, args=(cmd.split()),).start()


def draw_box(title, value):
    width = max(len(title), max_length(value))

    draw_line(width)
    draw_side(title, width)
    draw_line(width)
    for line in value:
        if line == '-':
            draw_line(width)
        else:
            draw_side(line, width)
    draw_line(width)


def draw_side(text, width):
    print_format = '{0:<%s}' % width
    print('| ' + print_format.format(text) + ' |')


def draw_line(width):
    print('+' + '-' * (width + 2) + '+')


def max_length(strings):
    result_length = 0
    for text in strings:
        length = len(text)
        if result_length < length:
            result_length = length

    return result_length
