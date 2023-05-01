# _*_ coding: utf-8 _*_
import environment
import util
import os
import subprocess

# Game Define
CATS = 'C.A.T.S.'
COOKIE_RUN = 'CookieRun'
GAME = {
    CATS: 'CATS.txt,com.zeptolab.cats.google',
    COOKIE_RUN: 'CookieRun.txt,com.devsisters.CookieRunForKakao'
}


def select_menu():
    menu_array = list()
    menu_array.append('1. %s Start' % CATS)
    menu_array.append('2. %s Stop' % CATS)
    menu_array.append('-')
    menu_array.append('3. %s Start' % COOKIE_RUN)
    menu_array.append('4. %s Stop' % COOKIE_RUN)
    menu_array.append('-')
    menu_array.append('X. All Stop')
    menu_array.append('C. Check Run')
    title = 'AutoScript - v%s' % environment.VERSION
    util.draw_box(title, menu_array)

    # noinspection PyBroadException
    try:
        select = input('Select : ')
    except:
        select = None

    if select is None or select == '':
        for game in GAME.keys():
            start(game)
    else:
        if type(select) == int:
            select = str(select)

        commands = list(select)
        for element in commands:
            if element == 'c' or element == 'C':
                check()
            elif element == 'x' or element == 'X':
                for game in GAME.keys():
                    stop(game)
            elif type(element) == int or element.isdigit():
                num = int(element)
                if num == 1:
                    start(CATS)
                elif num == 2:
                    stop(CATS)
                elif num == 3:
                    start(COOKIE_RUN)
                elif num == 4:
                    stop(COOKIE_RUN)

    print('')
    select_menu()


def start(game_name):
    filename, package_name = GAME[game_name].split(',')

    running_device = find_device(package_name)

    print_array = list()
    print_array.append('Game : %s' % game_name)
    print_array.append('Device : %s' % running_device)

    if running_device is not None:
        device_size = get_device_size(running_device)
        stop_message = stop(game_name, running_device, False)
        print_array += stop_message
        make_script(filename, device_size)
        print('')
        util.draw_box('Start Script.', print_array)
        start_script(running_device, filename)


def stop(game_name, device_name=None, when_menu_call=True):
    package_name = GAME[game_name].split(',')[1]

    return_array = list()
    print_array = list()

    if device_name is None:
        running_device = find_device(package_name)
    else:
        running_device = device_name

    print_array.append('Game : %s' % game_name)
    print_array.append('Device : %s' % running_device)

    if running_device is not None:
        kill_count, kill_messages = stop_script(running_device)
        if kill_count == 0:
            message = 'Run : None'
            if when_menu_call:
                print_array.append(message)
            else:
                return_array.append(message)
        else:
            if when_menu_call:
                print_array += kill_messages
            else:
                return_array += kill_messages

    if when_menu_call:
        print('')
        util.draw_box('Stop Script.', print_array)
    else:
        return return_array


def check():
    for game in GAME.keys():
        print_array = list()
        game_data = GAME[game].split(",")
        package_name = game_data[1]
        running_device = find_device(package_name)

        print_array.append('Game : %s' % game)
        print_array.append('Device : %s' % running_device)

        if running_device is not None:
            running_count, running_pids = check_script(running_device)
            if running_count == 0:
                running_pids = list()

            print_array.append('Run : %s' % ",".join(running_pids))

        print('')
        util.draw_box('Check Script.', print_array)


def find_device(package_name):
    call_result = util.get_call_result('adb devices').decode("utf-8")
    lines = call_result.splitlines()
    for line in lines:
        divide = line.split('\t')
        if len(divide) == 2 and divide[1] == 'device':
            if is_running(package_name, divide[0]):
                return divide[0]

    for line in lines:
        divide = line.split('\t')
        if len(divide) == 2 and divide[1] == 'device':
            if is_install(package_name, divide[0]):
                return divide[0]

    return None


def is_running(package_name, device):
    if environment.BACKGROUND_RUN_CHECK:
        # 앱이 실제로 동작하고 있는지 체크
        running_check_commend = 'adb -s %s shell ps' % device
        call_result = util.get_call_result(running_check_commend).decode("utf-8")
        for line in call_result.splitlines():
            if package_name in line:
                return True
    else:
        # 앱이 독작은 하는데, 백그라운드 인지 체크
        running_check_commend = 'adb -s %s shell dumpsys window windows' % device
        call_result = util.get_call_result(running_check_commend).decode('utf-8')
        for line in call_result.splitlines():
            if 'mCurrentFocus' in line and package_name in line:
                return True

    return False


def is_install(package_name, device):
    # 앱이 설치가 되어 있는지 체크
    running_check_commend = 'adb -s %s shell pm list packages -f' % device
    call_result = util.get_call_result(running_check_commend).decode("utf-8")
    for line in call_result.splitlines():
        if package_name in line:
            return True

    return False


def get_device_size(device):
    size_check_commend = 'adb -s %s shell wm size' % device
    call_result = util.get_call_result(size_check_commend).decode("utf-8")
    divide = call_result.split(':')
    if len(divide) == 2:
        return parse_screen_size(divide[1])

    # 오래된 단말들을 위하여 예전방식으로 한번 더 호출
    size_check_commend = 'adb -s %s shell dumpsys window' % device
    call_result = util.get_call_result(size_check_commend).decode("utf-8")
    find_result = list(filter(lambda x: 'Display:' in x, call_result.splitlines()))
    for line in find_result:
        cur_size = list(filter(lambda x: 'cur=' in x, line.split(' ')))[0]
        size = cur_size.split('=')[1]
        return parse_screen_size(size)

    return environment.DEFAULT_SCREEN_SIZE


def parse_screen_size(screen_size):
    size = screen_size.split('x')
    left = int(size[0].replace(' ', ''))
    right = int(size[1].replace(' ', ''))
    width = min(left, right)
    height = max(left, right)
    return [width, height]


def make_script(filename, device_size):
    width = 0
    height = 0

    file_path = os.path.join(environment.DATA_FOLDER, filename)
    file = open(file_path, mode='r', encoding='utf-8')

    for line in file:
        if 'SIZE' in line:
            divide = line.split(' ')
            height = divide[1]
            width = divide[2]
            break

    if width == 0 or height == 0:
        return False

    if not os.path.isdir(environment.TEMP_FOLDER):
        os.mkdir(environment.TEMP_FOLDER)
    output_file = open(os.path.join(environment.TEMP_FOLDER, filename), 'w')

    output_file.write('type= user\n')
    output_file.write('start data >>\n')

    width_ratio = float(min(device_size[0], device_size[1])) / float(width)
    height_ratio = float(max(device_size[0], device_size[1])) / float(height)

    for line in file:
        if 'CLICK' in line:
            divide = line.split(' ')
            resize_x = int(int(divide[1]) * width_ratio)
            resize_y = int(int(divide[2]) * height_ratio)
            output_file.write('Tap(%s,%s)\n' % (resize_x, resize_y))
        elif 'SLEEP' in line:
            divide = line.split(' ')
            output_file.write('UserWait(%s)\n' % int(divide[1]))
        elif 'REPEAT' in line:
            divide = line.split(' ')
            count = int(divide[4])
            for repeat in range(0, count):
                resize_x = int(int(divide[1]) * width_ratio)
                resize_y = int(int(divide[2]) * height_ratio)
                output_file.write('Tap(%s,%s)\n' % (resize_x, resize_y))
                output_file.write('UserWait(%s)\n' % int(divide[3]))

    output_file.close()

    return True


def start_script(device, filename):
    copy_commend = 'adb -s %s push %s /mnt/sdcard/' % (device, os.path.join(environment.TEMP_FOLDER, filename))
    subprocess.Popen(copy_commend, shell=True, stdout=subprocess.PIPE)

    monkey_commend = 'adb -s %s shell monkey -f /mnt/sdcard/%s 2147483647' % (device, filename)
    subprocess.Popen(monkey_commend, shell=True, stdout=subprocess.PIPE)


def stop_script(device):
    kill_messages = list()

    get_commend = 'adb -s %s shell ps' % device
    call_result = util.get_call_result(get_commend).decode("utf-8")
    kill_count = 0
    for line in call_result.splitlines():
        if environment.MONKEY in line:
            replace = " ".join(line.split())
            divide = replace.split(' ')
            kill_commend = 'adb -s %s shell kill %s' % (device, str(divide[1]))
            subprocess.call(kill_commend, shell=True)
            kill_count += 1
            kill_messages.append('Stop : ' + divide[1])

    return kill_count, kill_messages


def check_script(device):
    running_pids = list()

    get_commend = 'adb -s %s shell ps' % device
    call_result = util.get_call_result(get_commend).decode("utf-8")
    running_count = 0
    for line in call_result.splitlines():
        if environment.MONKEY in line:
            replace = " ".join(line.split())
            divide = replace.split(' ')
            running_count += 1
            running_pids.append(divide[1])

    return running_count, running_pids


if __name__ == '__main__':
    select_menu()
