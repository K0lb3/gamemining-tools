import os
import re
import subprocess


def main():
    src_path = input('Path to the source code folder that holds the source code that specifies the proto decoding.')
    if not os.path.exists(src_path):
        print('Invalid path, you may have to replace \ with \\')
        main()
    print('Collecting data from the source code...')
    configs, enums = CollectProtoData(src_path)
    print('Found %s buffers and %s enums'%(len(configs), len(enums)))

    dst_path = input('Where do you want to save the buffer files?')
    os.makedirs(dst_path, exist_ok=True)
    generateProtos(configs, enums, dst_path, dst_path+'_py')


reProtoContract = re.compile(r'\[[^\]]*ProtoContract\(Name\s*=\s*"(.+?)"\)\]')
reProtoMember = re.compile(r"\s*\[ProtoMember\((\d+),\s*(.+?)\)\]")
reProtoMemberKwargs = re.compile(r"\s*(.+?)\s*=(.+?)[,\)$]")
    #r'\s+\[ProtoMember\((\d+?),\s*DataFormat\s*=\s*DataFormat\.(.+?),\s*(IsRequired\s*=\s*true,\s*)?Name\s*=\s*"(.+?)"\)\]')
reProtoMemberTyp = re.compile(r'\s*(public|privat)\s+(.+?)\s+(.+)')
reProtoEnum = re.compile(r'\s+\[ProtoEnum\(Name\s*=\s*"(.+?)",\s*Value\s*=\s*(\d+)\)\]')


def CollectProtoData(mypath):
    """Extracts all protobuf configurations from the source files in the given path.
    :param mypath: path to the source files
    :return: (configs, enums)
    """
    files = os.listdir(mypath)

    # enum
    configs = {}
    enums = {}

    for f in files:
        # print(f)
        try:
            with open(os.path.join(mypath, f), "rt", encoding='utf8') as f:
                # find contract start and decide if enum or config
                for line in f:
                    match = reProtoContract.findall(line)
                    if match:
                        name = match[0]
                        if 'enum' in f.readline():
                            enums[name] = {}
                            for line in f:
                                match = reProtoEnum.match(line)
                                if match:
                                    enums[name][match[2]] = match[1]
                        else:
                            configs[name] = {}
                            for line in f:
                                match = reProtoMember.match(line)
                                if match:
                                    # /
                                    # 0-all, 1-number, 2-DataFormat, 3-Required, 4-name
                                    # 2
                                    #	1-typ, 2-name
                                    match2 = reProtoMemberTyp.findall(f.readline())[0]
                                    kwargs = {key:val.strip('"') for key,val in reProtoMemberKwargs.findall(match[2]+',')}
                                    configs[name][match[1]] = {
                                        'num': match[1],
                                        'name': kwargs['Name'],
                                        'required': 'IsRequired' in kwargs and kwargs['IsRequired'] == 'true',
                                        'dataformat': kwargs['DataFormat'],
                                        'type': match2[1]
                                    }

        except PermissionError:
            print('PermissionError')

    return (configs, enums)


#   functions that convert the given data into protobuffers
def generateProtos(ctypes, cenums, fpath, pypath=False):
    global enums
    global configs
    enums = cenums
    configs = ctypes
    os.makedirs(fpath, exist_ok=True)
    for key, items in ctypes.items():
        if 'ConfigData' == key[:10]:
            generateProto(key, items, fpath)
    if pypath:
        generateProtoPy(fpath, pypath)


def generateProto(name, items, fpath):
    open(
        file=os.path.join(fpath, '%s.proto' % name),
        mode='wt',
        encoding='utf8'
    ).write(
        '\n'.join([
            'syntax = "proto%s";' % 2,
            'package %s;' % name,
            generateProtoMessage(name, items),
            ''
        ])
    )


def generateProtoVarType(var):
    required = 'required' if var['required'] else 'optional'
    typ = 'variant'
    if 'type' in var:
        typ = var['type']
        # list?
        if typ[:5] == 'List<':
            required = 'repeated'
            typ = typ[5:-1]
        # typ fix
        if typ in ['string', 'bool', 'float', 'double']:
            pass
        elif typ == 'int':
            typ = 'int32'
        elif typ == 'uint':
            typ = 'uint32'
        elif typ == 'long':
            typ = 'int64'
        elif typ == 'ulong':
            typ = 'uint64'
        elif typ in enums:  # ~enum ~ atm as int
            typ = 'ENUM%s' % typ
        elif typ in configs:
            typ = 'SUB%s' % typ
        else:
            if '.' in typ:
                print(typ)
                var['type'] = typ.rsplit('.',1)[1]
                return generateProtoVarType(var)
            print('Unknown Var Type,', typ)
            typ = 'uint32'
    else:
        typ = 'string'  # if var['format']==0 else 'variant'

    return '{required} {type}'.format(
        required=required,
        type=typ,
    )


def usedSpecialTypes(items):
    # print(items)
    ltypes = set([
        item['type'] if item['type'][-1] != '>' else item['type'][5:-1]
        for index, item in items.items()
        if 'type' in item
    ])  # remove list and remove copies
    return [typ for typ in ltypes if typ not in ['string', 'int', 'bool']]


def generateProtoEnum(ename):
    return '\n'.join([
        'enum ENUM%s {' % ename,
        *[
            '	{name} = {index};'.format(
                name=sename,  # generateEName(sename[len(ename):]),#'ArmyTag_None' -> None
                index=str(index)
            )
            for index, sename in enums[ename].items()
        ],
        '}',
        ''
    ])


def generateProtoMessage(key, items, syntax=2, _main=True, used_subs=[]):
    if _main:
        used_subs = []

    ret = []
    for typ in usedSpecialTypes(items):
        if typ in used_subs:
            # print(key,'SUB',typ)
            continue
        if typ in enums:
            # print(key,'ENUM',typ)
            ret.append(generateProtoEnum(typ))
            used_subs.append(typ)
        elif typ in configs:
            # print(key,'SUB',typ)
            ret.append(generateProtoMessage('SUB%s' % typ, configs[typ], _main=False, used_subs=used_subs))
            used_subs.append(typ)

    ret.extend([
        'message %s {' % key,
        *[
            '	{typ} {name} = {index};'.format(
                typ=generateProtoVarType(item),
                name=item['name'],
                index=item['num']
            )
            for index, item in sorted(list(items.items()), key=lambda item: int(item[0]))
        ],
        '}'
    ])
    if _main:
        ret.extend([
            '',
            'message Items {',
            '	repeated %s items = 1;' % key,
            '}'
        ])
    return '\n'.join(ret)


def generateProtoPy(src, dest):
    names = []
    os.makedirs(dest, exist_ok=True)
    for fp in os.listdir(src):
        if '.proto' == fp[-6:] and fp[0] != '_':
            result = subprocess.run([
                "protoc",
                "--proto_path=%s" % src,
                "--python_out=%s" % dest,
                os.path.join(src, fp)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            if 'already defined' in str(result):
                print(str(result)[str(result).find('stderr'):])
            else:
                names.append(fp[:-6])

    # init
    open(os.path.join(dest, '__init__.py'), 'wt', encoding='utf8').write(
        '\n'.join([
            'from .%s_pb2 import Items as %s' % (name, name)
            for name in [fp[:-7] for fp in os.listdir(dest) if fp[0] != '_']
        ])
    )

if __name__ == '__main__':
    main()