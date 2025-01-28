import base64
import re
import pefile
import yara
import struct

RULE_SOURCE = """rule LummaBuildId
{
    meta:
        author = "YungBinary"
    strings:
        $chunk_1 = {
            8B ( 1D | 0D | 15 ) [4]
            C7 [5-10]
            C7 [5-10]
            C7 [5-10]
            C7 [5-10]
            C7 [5-10]
            C7 [5-10]
            C7 [5-10]
            C7
		}
    condition:
        $chunk_1
}"""


def yara_scan(raw_data):
    yara_rules = yara.compile(source=RULE_SOURCE)
    matches = yara_rules.match(data=raw_data)

    for match in matches:
        for block in match.strings:
            for instance in block.instances:
                yield block.identifier, instance.offset


def is_base64(s):
    pattern = re.compile("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$")
    if not s or len(s) < 1:
        return False
    else:
        return pattern.match(s)


def extract_strings(data, minchars):
    endlimit = b"8192"
    apat = b"([\x20-\x7e]{" + str(minchars).encode() + b"," + endlimit + b"})\x00"
    strings = [string.decode() for string in re.findall(apat, data)]
    return strings


def get_base64_strings(str_list):
    base64_strings = []
    for s in str_list:
        if is_base64(s):
            base64_strings.append(s)
    return base64_strings


def get_rdata(pe, data):
    rdata = None
    section_idx = 0
    for section in pe.sections:
        if section.Name == b".rdata\x00\x00":
            rdata = pe.sections[section_idx].get_data()
            break
        section_idx += 1
    return rdata


def xor_data(data, key):
    decoded = bytearray()
    for i in range(len(data)):
        decoded.append(data[i] ^ key[i % len(data)])
    return decoded


def contains_non_printable(byte_array):
    for byte in byte_array:
        if not chr(byte).isprintable():
            return True
    return False


def extract_config(data):
    config_dict = {"C2": []}

    try:
        lines = data.decode().split("\n")
        for line in lines:
            try:
                if "." in line and len(line) > 2:
                    if not contains_non_printable(line):
                        config_dict["C2"].append(line)
            except Exception:
                continue
    except Exception:
        pass

    # If no C2s with the old method,
    # try with newer version xor decoding
    if not config_dict["C2"]:

        # try to load as a PE
        pe = None
        image_base = None
        try:
            pe = pefile.PE(data=data)
            image_base = pe.OPTIONAL_HEADER.ImageBase
        except Exception:
            pass

        try:
            if pe is not None:
                rdata = get_rdata(pe, data)
                if rdata is not None:
                    strings = extract_strings(rdata, 44)
                else:
                    strings = extract_strings(data, 44)
            else:
                strings = extract_strings(data, 44)

            base64_strings = get_base64_strings(strings)
            for base64_str in base64_strings:
                try:
                    decoded_bytes = base64.b64decode(base64_str, validate=True)
                    encoded_c2 = decoded_bytes[32:]
                    xor_key = decoded_bytes[:32]
                    decoded_c2 = xor_data(encoded_c2, xor_key)

                    if not contains_non_printable(decoded_c2):
                        config_dict["C2"].append(decoded_c2.decode())
                except Exception:
                    continue
            
            if config_dict["C2"] and pe is not None:
                # If found C2 servers try to find build ID
                for match in yara_scan(data):
                    try:
                        rule_str_name, offset = match
                        build_id_data_rva = struct.unpack('i', data[offset + 2 : offset + 6])[0]
                        build_id_dword_offset = pe.get_offset_from_rva(build_id_data_rva - image_base)
                        build_id_dword_rva = struct.unpack('i', data[build_id_dword_offset : build_id_dword_offset + 4])[0]
                        build_id_offset = pe.get_offset_from_rva(build_id_dword_rva - image_base)
                        build_id = pe.get_string_from_data(build_id_offset, data)
                        if not contains_non_printable(build_id):
                            config_dict["Build ID"] = build_id.decode()
                    except Exception:
                        continue

        except Exception:
            return

    return config_dict


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "rb") as f:
        print(extract_config(f.read()))
