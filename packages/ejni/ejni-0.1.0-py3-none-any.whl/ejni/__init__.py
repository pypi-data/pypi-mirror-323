import argparse
import json
import multiprocessing
from collections import Counter, namedtuple
from datetime import datetime
from io import BytesIO
from typing import Iterator, List

from apkutils import APK
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

from ejni import utils

SoFile = namedtuple("SoFile", ["name", "data"])

JNI_COMMON = {
    "JNI_OnLoad": ["jint", "JavaVM * vm, void * reserved"],
    "JNI_OnUnload": ["void", "JavaVM * vm, void * reserved"],
}

__COMMON__ = [
    {"mangle": "JNI_OnLoad", "ret": "jint", "args": ["JavaVM * vm", "void * reserved"]},
    {
        "mangle": "JNI_OnUnload",
        "ret": "void",
        "args": ["JavaVM * vm", "void * reserved"],
    },
]


class JNIMethod:
    def __init__(self, jclass, name, descriptor, static=False, overload=False):
        self.jclass = jclass  # fullname: e.g com.evilpan.Foo
        self.name = name  # method name
        method_args, ret = descriptor[1:].rsplit(")", 1)
        self.args = str(method_args).split()  # list of smali type, space splited
        self.ret = str(ret)  # smali type
        self.descriptor = f"({''.join(self.args)}){self.ret}"
        self.static = static
        self.overload = overload

    @property
    def native_name(self):
        """
        return crosponding native C symbol name
        https://docs.oracle.com/en/java/javase/16/docs/specs/jni/design.html
        """
        name = utils.escape(self.jclass + "." + self.name)
        name = "Java_" + name.replace(".", "_")
        if self.overload:
            sig = "".join(self.args)
            sig = utils.escape(sig)
            name = name + "__" + sig
        return name

    @property
    def native_args(self):
        # NOTE: ghidra pointer and type require space inside
        native_args_list = [("JNIEnv *", "env")]
        if self.static:
            native_args_list.append(("jclass", "clazz"))
        else:
            native_args_list.append(("jobject", "thiz"))
        return native_args_list + [
            (utils.get_type(arg), f"a{i + 1}") for i, arg in enumerate(self.args)
        ]

    @property
    def native_args_list(self) -> List[str]:
        return [f"{t} {n}" for t, n in self.native_args]

    @property
    def native_ret(self):
        return utils.get_type(self.ret)

    @property
    def as_dict(self):
        return {self.native_name: [self.native_ret, ", ".join(self.native_args_list)]}

    @property
    def as_json(self):
        return {
            "mangle": self.native_name,
            "ret": self.native_ret,
            "args": self.native_args_list,
            "name": self.name,
            "sig": self.descriptor,
        }

    def __repr__(self):
        return f"{'static ' if self.static else ''}{self.name}({' '.join(self.args)}){self.ret}"

    def __str__(self):
        return f"JNIEXPORT {self.native_ret} JNICALL {self.native_name} ({', '.join(self.native_args_list)})"


def get_exported_functions(filedata):
    out = {}
    elffile = ELFFile(BytesIO(filedata))
    symbol_tables = [
        (idx, s)
        for idx, s in enumerate(elffile.iter_sections())
        if isinstance(s, SymbolTableSection)
    ]

    for _, section in symbol_tables:
        for _, symbol in enumerate(section.iter_symbols()):
            if (
                symbol.entry.st_info.type == "STT_FUNC"
                and symbol.entry.st_shndx != "SHN_UNDEF"
            ):
                out[symbol.name] = symbol["st_value"]
    return out


def extract_so_files(apkfile: str) -> Iterator[SoFile]:
    from zipfile import ZipFile

    z = ZipFile(apkfile)
    for info in z.infolist():
        if info.filename.endswith(".so") and info.filename.startswith("lib/arm64-v8a"):
            yield SoFile(info.filename, z.read(info))


def parse_so(sofile: SoFile):
    try:
        funcs = get_exported_functions(sofile.data)
    except Exception as e:
        print(f"skip library {sofile.name}: {e}")
        funcs = {}
    return {k: v for k, v in funcs.items() if k.startswith("Java_") or k in JNI_COMMON}


def parse_dex_file(dex_file):
    dexInfo = {}
    count = 0

    for dex_class in dex_file.classes:
        count += 1
        try:
            dex_class.parseData()
        except IndexError:
            continue

        jni_methods = []
        names = []

        for method in dex_class.data.methods:
            # 查找 native 方法
            access = utils.get_access_flags_string(method.access)
            if "native" not in access:
                continue

            # 生成 JNI 方法
            jclass = method.id.cname.decode()[1:-1].replace("/", ".")
            name = method.id.name.decode()
            descriptor = method.id.desc.decode()
            jni_mehtod = JNIMethod(jclass, name, descriptor, static="static" in access)
            if jni_mehtod is None:
                continue
            jni_methods.append(jni_mehtod)
            names.append(jni_mehtod.name)

        if not jni_methods:
            continue

        n = Counter(names)
        for it in jni_methods:
            if n.get(it.name, 0) > 1:
                it.overload = True

        class_name = jni_methods[0].jclass
        if class_name not in dexInfo:
            dexInfo[class_name] = []

        for it in jni_methods:
            dexInfo[class_name].append(it.as_json)

    # print(json.dumps(dexInfo, indent=4))
    return count, dexInfo


def parse_apk(apkfile, workers, fn_match=None, outfile=None):
    dexInfo = {"__COMMON__": __COMMON__}
    num_classes = 0

    # TODO: 如果有多个 Dex 文件，是否会影响速度，待测试
    apk = APK.from_file(apkfile)
    dex_files = apk.dex_files

    with multiprocessing.Pool(workers) as pool:
        result = pool.imap(parse_dex_file, dex_files)
        for count, res in result:
            if count == 0:
                continue
            num_classes += count

            for className, methodData in res.items():
                if fn_match and not fn_match(className):
                    continue
                dexInfo.update({className: methodData})

    soInfo = {}
    soFiles = list(extract_so_files(apkfile))
    for soFile in soFiles:
        possible_symbols = parse_so(soFile)
        if possible_symbols:
            soInfo[soFile.name] = possible_symbols

    output = {"dexInfo": dexInfo, "soInfo": soInfo}
    if not outfile:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("apk", help="/path/to/apk")
    parser.add_argument(
        "-j",
        dest="workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="parse apk with multiple workers(processes)",
    )
    parser.add_argument(
        "-o", dest="outfile", help="save JNI methods as formatted json file"
    )
    args = parser.parse_args()

    parse_apk(args.apk, args.workers, outfile=args.outfile)
