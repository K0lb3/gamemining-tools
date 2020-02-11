import os
import shutil

Original_Filename = b'O\x00r\x00i\x00g\x00i\x00n\x00a\x00l\x00F\x00i\x00l\x00e\x00n\x00a\x00m\x00e\x00\x00\x00'
def get_name(data):
    index = data.find(Original_Filename)
    if index != -1:
        data = data[index + len(Original_Filename):]
        index = data.find(b'\x00\x00')
        return data[:index][::2].decode()
    return False

for fp in list(os.listdir()):
    try:
        name = get_name(open(fp, 'rb').read())
        name, ext = os.path.splitext(name)
    except:
        continue
    i=0
    while os.path.exists(f"{name}{i}{ext}"):
        i+=1
    if name and name != fp:
        try:
            print(fp, f"{name}{i}{ext}")
            shutil.move(fp, f"{name}{i}{ext}")
        except:
            pass
    else:
        try:
            os.unlink(fp)
        except:
            pass