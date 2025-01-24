# from androguard.decompiler.util import TYPE_DESCRIPTOR
TYPE_DESCRIPTOR = {
    "V": "void",
    "Z": "boolean",
    "B": "byte",
    "S": "short",
    "C": "char",
    "I": "int",
    "J": "long",
    "F": "float",
    "D": "double",
}


def get_type(atype):
    """
    Retrieve the java type of a descriptor (e.g : I -> jint)
    """
    res = TYPE_DESCRIPTOR.get(atype)
    if res:
        if res == "void":
            return res
        else:
            return "j" + res
    if atype[0] == "L":
        if atype == "Ljava/lang/String;":
            res = "jstring"
        else:
            res = "jobject"
    elif atype[0] == "[":
        if len(atype) == 2 and atype[1] in "ZBSCIJFD":
            res = TYPE_DESCRIPTOR.get(atype[1])
        else:
            res = "object"
        res = f"j{res}Array"
    else:
        print('Unknown descriptor: "%s".', atype)
        res = "void"
    return res


def mangle_unicode(input_str):
    out = ""
    for s in input_str:
        i = ord(s)
        if 0 <= i < 128:
            out += s
        else:
            out += f"_{i:04x}"
    return out


def escape(name: str):
    name = name.replace("_", "_1")
    name = name.replace(";", "_2")
    name = name.replace("[", "_3")
    name = mangle_unicode(name)
    name = name.replace("/", "_")
    return name


# https://source.android.com/devices/tech/dalvik/dex-format#access-flags
ACCESS_FLAGS = {
    0x1: "public",
    0x2: "private",
    0x4: "protected",
    0x8: "static",
    0x10: "final",
    0x20: "synchronized",
    0x40: "bridge",
    0x80: "varargs",
    0x100: "native",
    0x200: "interface",
    0x400: "abstract",
    0x800: "strictfp",
    0x1000: "synthetic",
    0x4000: "enum",
    0x8000: "unused",
    0x10000: "constructor",
    0x20000: "synchronized",
}


def get_access_flags_string(access_flags) -> str:
    """
    Return the access flags string of the method

    A description of all access flags can be found here:
    https://source.android.com/devices/tech/dalvik/dex-format#access-flags

    :rtype: string
    """

    def to_str(value: int) -> str:
        """
        Transform an access flag field to the corresponding string

        :param value: the value of the access flags
        :type value: int

        :rtype: string
        """
        flags = []
        for k, v in ACCESS_FLAGS.items():
            if (k & value) == k:
                flags.append(v)

        return " ".join(flags)

    access_flags_string = to_str(access_flags)

    if access_flags_string == "" and access_flags != 0x0:
        access_flags_string = "0x%x" % access_flags
    return access_flags_string
