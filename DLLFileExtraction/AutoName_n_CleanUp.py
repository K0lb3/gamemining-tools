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

for fp in os.listdir():
    name = get_name(open(fp, 'rb').read())
    if name and name != fp:
        try:
            print(fp, name)
            shutil.move(fp, name)
        except:
            pass
    else:
        try:
            os.unlink(fp)
        except:
            pass