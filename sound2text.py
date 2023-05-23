import os
import re
import time
import ffmpeg
from faster_whisper import WhisperModel
import shutil
import traceback


spath = "z:/ASMR"
dpath = spath + '_short'
txtpath = spath + '_txt'
errpath = spath + '_err'
model_size = "large-v2"
whisper_model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
wrongpath = os.path.join(dpath, 'wrong.txt')
name_length = 100
wokers_number = 2


def move_file(src_path: str, dst_path: str):
    shutil.move(src_path, dst_path)

def add_line_to_file(file_name, content):
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write('')
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines.append(str(content) + '\n')
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))


def get_media_info(filename):
    try:
        result = ffmpeg.probe(filename)
        print(result)
        if result:
            return result
        else:
            try:
                os.remove('null')
                ffmpeg.input(filename).output('null', format='md5').run(capture_stdout=True)
                return True
            except ffmpeg.Error as e:
                return False
    except ffmpeg.Error as e:
        return False


# 获取本地时间
def get_local_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_relative_path(folder1, folder2):
    return os.path.relpath(folder2, folder1)


def get_all_file_paths_abs(directory_path, file_type='all'):
    file_paths = []
    for root, directories, files in os.walk(directory_path):
        for filename in files:
            if file_type == 'all':
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            if file_type == 'audio':
                if filename.endswith(".mp3") or filename.endswith(
                        ".m4a") or filename.endswith(
                    ".wav") or filename.endswith(
                    ".wma") or filename.endswith(
                    ".flac") or filename.endswith(".aac"):
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
            elif file_type == 'video':
                if filename.endswith(".mp4") or filename.endswith(
                        ".m4v") or filename.endswith(
                    ".mkv") or filename.endswith(
                    ".wmv") or filename.endswith(
                    ".mov") or filename.endswith(".avi"):
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
            elif file_type == 'picture':
                if filename.endswith(".jpg") or filename.endswith(
                        ".jpeg") or filename.endswith(
                    ".gif") or filename.endswith(
                    ".bmp") or filename.endswith(".png"):
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
    return file_paths


def get_all_file_paths_rel(directory_path, file_type='all'):
    file_paths = []
    for root, directories, files in os.walk(directory_path):
        for filename in files:
            if file_type == 'all':
                filepath_abs = os.path.join(root, filename)
                filepath_rel = get_relative_path(directory_path, filepath_abs)
                file_paths.append(filepath_rel)
            if file_type == 'audio':
                if filename.endswith(".mp3") or filename.endswith(
                        ".m4a") or filename.endswith(
                    ".wav") or filename.endswith(
                    ".wma") or filename.endswith(
                    ".flac") or filename.endswith(".aac"):
                    filepath_abs = os.path.join(root, filename)
                    filepath_rel = get_relative_path(directory_path,
                                                     filepath_abs)
                    file_paths.append(filepath_rel)
            elif file_type == 'video':
                if filename.endswith(".mp4") or filename.endswith(
                        ".m4v") or filename.endswith(
                    ".mkv") or filename.endswith(
                    ".wmv") or filename.endswith(
                    ".mov") or filename.endswith(".avi"):
                    filepath_abs = os.path.join(root, filename)
                    filepath_rel = get_relative_path(directory_path,
                                                     filepath_abs)
                    file_paths.append(filepath_rel)
            elif file_type == 'picture':
                if filename.endswith(".jpg") or filename.endswith(
                        ".jpeg") or filename.endswith(
                    ".gif") or filename.endswith(
                    ".bmp") or filename.endswith(".png"):
                    filepath_abs = os.path.join(root, filename)
                    filepath_rel = get_relative_path(directory_path,
                                                     filepath_abs)
                    file_paths.append(filepath_rel)
    return file_paths


def cut_audio_file(sfileurl, startsec, endsec):
    if os.path.exists(sfileurl):
        filepath_rel = get_relative_path(spath, sfileurl)
        ori_audio_file_abs = os.path.join(spath, filepath_rel)
        cut_audio_file_abs = os.path.join(dpath, filepath_rel.split(".")[0] + '.mp3')
        txt_filepath = os.path.join(txtpath, filepath_rel.split(".")[0] + '.txt')
        ddirname, dfilename = os.path.split(cut_audio_file_abs)
        dfile_name = dfilename.split(".")[0] + '.mp3'
        dfileurl_abs = os.path.join(ddirname, dfile_name)
        if os.path.exists(cut_audio_file_abs):
            # os.remove(dfileurl_abs)
            if os.path.getsize(cut_audio_file_abs) > 0:
                return cut_audio_file_abs
            else:
                os.remove(cut_audio_file_abs)
        if not os.path.exists(ddirname):
            try:
                os.makedirs(ddirname)
            except:
                print(f"[-]Fatal error! Can not make folder '{ddirname}'")
                os._exit(0)
        if get_media_info(ori_audio_file_abs):
            try:
                stream = ffmpeg.input(ori_audio_file_abs, ss=startsec)
                stream = ffmpeg.output(stream, cut_audio_file_abs, to=endsec, ac=1)
                ffmpeg.run(stream)
            except Exception as e:
                print(f"[-]Fatal error! file '{sfileurl}' is bad")
                # print(e)
                add_line_to_file(wrongpath, cut_audio_file_abs)
                return
        else:
            print(f"[-]Fatal error! file '{cut_audio_file_abs}' is bad")
            # print(e)
            add_line_to_file(wrongpath, cut_audio_file_abs)
            return
    else:
        print(f"[-]Fatal error! Can not find file '{cut_audio_file_abs}'")
    return dfileurl_abs


def cut_audio_files(sfiles, startsec, endsec):
    files_paths = []
    for audio_file_url in sfiles:
        # audio_file_url = os.path.join(spath, audio_file_url)
        try:
            short_audio_file_paths = cut_audio_file(audio_file_url, startsec,
                                                    endsec)
            files_paths.append(short_audio_file_paths)
        except Exception as e:
            print(e)
        continue
    return files_paths


def text2title(input_str, length):
    # 只保留中文文字、英文字母及数字，其他都替换为下划线
    input_str = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '_', input_str)
    return input_str[:length]


def write_to_file(directory_path: str, content: str):
    ddirname, dfilename = os.path.split(directory_path)
    if not os.path.exists(ddirname):
        try:
            os.makedirs(ddirname)
        except:
            print(f"[-]Fatal error! Can not make folder '{ddirname}'")
            os._exit(0)
    with open(directory_path, "w", encoding='utf-8') as f:
        f.write(str(content))

def read_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return content

def sound2text(input_audio_file,startsec,endsec):  #input_audio_file 需要为相对路径
    ori_audio_file_abs = os.path.join(spath, input_audio_file)
    cut_audio_file_abs = os.path.join(dpath, input_audio_file.split(".")[0] + '.mp3')
    if not os.path.exists(cut_audio_file_abs):
        cut_audio_file_abs = cut_audio_file(ori_audio_file_abs, startsec, endsec)
    try:
        segments, info = whisper_model.transcribe(cut_audio_file_abs, beam_size=5, vad_filter=True)
        # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        if info.language != 'zh':
            return
        segments = list(segments)
        audio2text = " ".join([i.text for i in segments if i is not None])
    except Exception as e:
        print(e)
        return
    return audio2text
def sound2txt(input_audio_file,startsec,endsec):  #input_audio_file 需要为相对路径
    ori_audio_file_abs = os.path.join(spath, input_audio_file)
    txt_filepath = os.path.join(txtpath, input_audio_file.split(".")[0] + '.txt')
    err_filepath = os.path.join(errpath, input_audio_file)
    odirname, ofilename = os.path.split(ori_audio_file_abs)
    print(f"\033[1;35m{get_local_time()}=====开始识别{ofilename}==================")
    if os.path.exists(txt_filepath):
        if os.path.getsize(txt_filepath) > 0:
            print(f"\033[1;35m{get_local_time()}====={ofilename}txt存在，自动跳过=============")
            return False
        else:
            os.remove(txt_filepath)

    audio_text = sound2text(input_audio_file, startsec, endsec)
    if audio_text:
        print(f"\033[1;35m{get_local_time()}=====识别{ofilename}完毕==================")
        sdirname, sfilename = os.path.split(txt_filepath)
        if not os.path.exists(sdirname):
            try:
                os.makedirs(sdirname)
            except:
                print(f"[-]Fatal error! Can not make folder '{sdirname}'")
        write_to_file(txt_filepath, audio_text)
        print(f"\033[1;35m{get_local_time()}=====保存{sfilename}完毕==================")
        return True
    else:
        print(f"\033[1;35m{get_local_time()}=====未识别到中文文本==================")
        sdirname, sfilename = os.path.split(err_filepath)
        if not os.path.exists(sdirname):
            try:
                os.makedirs(sdirname)
            except:
                print(f"[-]Fatal error! Can not make folder '{sdirname}'")
                os._exit(0)
        move_file(ori_audio_file_abs, err_filepath)
        print(f"\033[1;35m{get_local_time()}=====未识别到中文文本==================")
        return False

def sounds2txt(spath_url, startsec, endsec): #input_audio_files 需要为相对路径
    audio_files_paths = get_all_file_paths_rel(spath_url, 'audio')
    for audio_files_path in audio_files_paths:
        sound2txt(audio_files_path,startsec,endsec)

def main():
    spath = input("请输入目录地址：")
    start_time = '00:01:00'
    end_time = '00:02:00'
    sounds2txt(spath, start_time, end_time)

if __name__ == '__main__':
    main()