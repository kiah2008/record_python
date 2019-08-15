# coding:utf8
import os
import time
import datetime
import threading

DEBUG_TEST = 1
MAX_FILE_DURATION = 30 * 60
CURRENT_STR_FORMAT = "%Y.%m.%d-%H:%M:%S"
CAMERA_FILE_PATH = "/sdcard/DCIM/Camera"

v_list = (
    "05:50:00",
    "05:49:00",
    "05:26:00"
)
pull_file_list = []
pull_file_index = 0
pull_file_ignore_count = 0
tid_file = threading.Thread


def exec_cmd(cmd=""):
    global CURRENT_STR_FORMAT
    time.sleep(0.4)
    ret = os.system(cmd)
    print("%s:exec cmd %d:%s" % (get_current_time_str(), ret, cmd))
    if ret != 0:
        print("!!!!!!!!!!!!!!!!!error:%s!" % cmd)


def schedule_job():
    global MAX_FILE_DURATION, tid_file, CURRENT_STR_FORMAT, v_list, pull_file_index, DEBUG_TEST, pull_file_ignore_count
    t_list = (
        "00:00:05",
        "00:00:05",
        "00:00:05"
    )

    if DEBUG_TEST:
        v_list = t_list
        MAX_FILE_DURATION = 4
    # get current file count, and ignore the current files before catch
    pull_video()
    pull_file_ignore_count = pull_file_index = len(pull_file_list)
    for file_ignore in pull_file_list:
        print("%s: ignore  the old file %s" % (get_current_time_str(), file_ignore))
    tid_file = threading.Thread(target=thread_file_cmd)
    tid_file.start()
    for (idx, vv) in enumerate(v_list):
        exec_cmd("adb shell input keyevent 4")
        exec_cmd("adb shell input keyevent 4")
        time_stamp = datetime.datetime.now()
        print("%s:let begin the %d video lens %s" % (time_stamp.strftime(CURRENT_STR_FORMAT), idx, vv))
        time_sec = cal_seconds(vv)
        handle_recording(time_sec)


def handle_recording(vv=0):
    global MAX_FILE_DURATION
    tt = vv
    rec_max = MAX_FILE_DURATION
    while vv > 0:
        if vv >= rec_max:
            tt = rec_max
            vv -= rec_max
        else:
            tt = vv
            vv = 0

        print("%s:handle recording duration is %d" % (get_current_time_str(), tt))
        # start recording
        exec_cmd("adb shell am start -a android.intent.action.MAIN -n com.android.camera/.Camera")

        exec_cmd("adb shell \"input keyevent KEYCODE_FOCUS\"")
        exec_cmd("adb shell \"input keyevent KEYCODE_CAMERA\"")
        time.sleep(tt)
        # stop recording
        exec_cmd("adb shell \"input keyevent KEYCODE_CAMERA\"")
        time.sleep(2)
        # exec_cmd("adb shell input keyevent 4")
        pull_video()


def get_current_time_str():
    global CURRENT_STR_FORMAT
    local_time = datetime.datetime.now()
    return local_time.strftime(CURRENT_STR_FORMAT)


def cal_seconds(duration=""):
    time_array = duration.split(":")
    if len(time_array) != 3:
        print("!!!!!!!!!!!!!!error, not time array")
        return
    print("duration is %s-%s-%s" % (time_array[0], time_array[1], time_array[2]))
    time_second = int(time_array[0]) * 3600 + int(time_array[1]) * 60 + int(time_array[2]);
    print("time is %d seconds" % time_second)
    return time_second


def thread_file_cmd():
    global pull_file_index, pull_file_ignore_count
    global pull_file_list
    global MAX_FILE_DURATION
    print("%s: begin file thread w/ %d" % (get_current_time_str(), MAX_FILE_DURATION))
    retry = 0

    while True:
        time.sleep(MAX_FILE_DURATION + MAX_FILE_DURATION / 30)
        if pull_file_index <= (len(pull_file_list) - 1):
            i = pull_file_index - pull_file_ignore_count
            print("%s: pull [%d] %s" % (get_current_time_str(), i, pull_file_list[pull_file_index]))
            exec_cmd("adb pull %s" % pull_file_list[pull_file_index])
            print("%s: pull done [%d] %s" % (get_current_time_str(), i, pull_file_list[pull_file_index]))
            exec_cmd("adb shell rm -rf %s" % pull_file_list[pull_file_index])
            pull_file_index = 1 + pull_file_index
            retry = 0
        else:
            remain_c = pull_video()
            if remain_c == pull_file_ignore_count:
                retry = 1 + retry
                print("%s: retry count %d" % (get_current_time_str(), retry))
                if retry == 3:
                    print("%s: finished", get_current_time_str())
                    break
            print("%s: no video recording (%d/%d - t%d)!" % (
            get_current_time_str(), pull_file_index, pull_file_ignore_count, remain_c))
            continue


def pull_video():
    global pull_file_list, CAMERA_FILE_PATH
    output = os.popen("adb shell ls %s" % CAMERA_FILE_PATH)
    file_str = output.read()
    file_list = file_str.split()
    for ifile in file_list:
        pull_file_str = "/".join([CAMERA_FILE_PATH, ifile])
        time_stamp = datetime.datetime.now()
        if pull_file_list.count(pull_file_str) > 0:
            # print("ignore %s" % pull_file_str)
            continue
        else:
            print("append %s" % pull_file_str)
            pull_file_list.append(pull_file_str)
    return len(file_list)


if __name__ == "__main__":
    schedule_job()
    print("good job!")
    tid_file.join()
    time_stamp = datetime.datetime.now()
    print("%s:bye!", time.strftime(CURRENT_STR_FORMAT))
