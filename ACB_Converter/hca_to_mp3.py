import subprocess
import shutil
import os
import sys
PATH = os.path.dirname(os.path.realpath(__file__))

LAME = os.path.join(PATH, "lame", "lame.exe")
HCATOWAV = os.path.join(PATH, "DereTore", "hca2wav.exe")

def convert_folder(src, dst=None):
    src = "D:\\Disassemlby\\WarOfTheVisions\\download\\streaming"
    dst = "D:\\Disassemlby\\WarOfTheVisions\\download\\streaming_ex_hca"
    if not dst:
        dst = src
    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        for fp in files:
            fp = os.path.join(root, fp)
            if True:#if os.path.splitext(fp)[1] == ".acb":
                try:
                    print(fp,end="\n")
                    fp, extension = os.path.splitext(fp)
                    name = os.path.basename(fp)
                    if extension == ".hca":
                        print(name,"hca to wav ", end = "")
                        hca_to_wav(f"{fp}.hca")
                        print(name," done\nwav to mp3 ", end = "")
                        wav_to_mp3(f"{fp}.wav",os.path.join(dst, f"{name}.mp3"))
                        print(name," done", end = "\n")
                except AssertionError:
                    continue
    

def acb_to_mp3(src, dst):
    temp_path = os.path.join(
        os.path.dirname(src),
        f"_acb_{os.path.basename(src)}"
    )
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    
    os.makedirs(dst, exist_ok=True)
    try:
        # 1. acbunzip
        print("acb2hca",end="")
        acb_unzip(src)
        print("-done",end="\n")


        # convert hca to wav and then to mp3
        for fp in os.listdir(temp_path):
            name, extension = os.path.splitext(fp)
            fp = os.path.join(temp_path, name)
            if extension == ".hca":
                print(name,"hca to wav", end = "")
                hca_to_wav(f"{fp}.hca")
                print(name," done, wav to mp3", end = "")
                wav_to_mp3(f"{fp}.wav",os.path.join(dst, f"{name}.mp3"))
                print(name," done", end = "\n")
    except:
        pass
    print(f"cleaning up temp path ({temp_path})")
    shutil.rmtree(temp_path)


def acb_unzip(src):
    result = subprocess.run([
        ACBUNZIP,
        src
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    # could fetch files from result.strerr
    if result.returncode != 0:
        raise AssertionError(f"Failed conversion of {src}")

def hca_to_wav(src):
    result = subprocess.run([
        HCATOWAV,
        src
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    # could fetch files from result.strerr
    if result.returncode != 0:
        raise AssertionError(f"Failed conversion of {src}")

def wav_to_mp3(src, dst):
    result = subprocess.run([
        LAME,
        src,
        dst
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    # could fetch files from result.strerr
    if result.returncode != 0:
        raise AssertionError(f"Failed conversion of {src}")


if __name__ == '__main__':
    convert_folder("","")
    if len(sys.argv) != 3:
        convert_folder(
            input("src: "),
            input("dst: ")
        )
    else:
        convert_folder(*sys.argv[1])