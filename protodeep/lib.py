from fnmatch import fnmatch

from rich.console import Console

from protodeep.blackboxprotobuf import decode_message, export_protofile
from protodeep.utils import strip_markups
from protodeep.internals import find_proto_schema, clean_schema


class ProtoDeepSchema():
    def __init__(self, schema: dict, values: dict):
        self.schema: dict = schema
        self.values: dict = values

    def export_protofile(self, filename: str, name: str="Schema"):
        export_protofile({name: self.schema}, filename)
        print(f"[+] Protofile {filename} created !")

    def export_protodeep(self, filename: str):
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump({
                "schema": self.schema,
                "values": self.values
            }, f)
        print(f"[+] Protodeep file {filename} created !")

    def compile_python(self, filename: str, export_protobuf: str, name: str="Schema"):
        from grpc_tools import protoc

        import uuid
        from pathlib import Path

        random_id = uuid.uuid4().hex[:20]
        random_name = f"{random_id}.proto"

        if filename == "default_pb2.py" and export_protobuf:
            filename = f"{export_protobuf.split('.')[:1][0]}_pb2.py"
        
        if not export_protobuf:
            self.export_protofile(random_name, name)
        else:
            import shutil
            shutil.copy(export_protobuf, random_name)
            
        compile_out_path = Path(filename)

        current_path = Path.cwd()
        command = [
            'grpc_tools.protoc',
            f'-I={current_path}',
            f'--python_out={current_path}',
            random_name
        ]
        status = protoc.main(command)
        if status:
            exit("[-] Python compilation failed. :(")

        if compile_out_path.exists() and compile_out_path.is_file():
            compile_out_path.unlink() # Living dangerous

        Path(f"{random_id}_pb2.py").rename(compile_out_path)
        Path(random_name).unlink()

        print(f"[+] Python file {compile_out_path} created !")

    def pretty_print(self, 
                    hide_empty=False,
                    match_any="",
                    match_keychain="",
                    match_value="",
                    filter_any="",
                    filter_keychain="",
                    filter_value=""):
        def _pretty_print(schema: dict[str, dict], parsed: dict, key_chain: str="", pretty_chain: str=""):
            for key,sub in schema.items():
                pkey = ""
                sname = ""
                skey = f"[sky_blue2]{key}[/sky_blue2]"
                if sname := sub.get("name"):
                    pkey = f"[wheat1]{sname}[/wheat1]"
                else:
                    pkey = f"[misty_rose3]{key}[/misty_rose3]"

                if sub.get("seen_repeated"):
                    if sname:
                        pkey = f"[wheat1]{sname}[][/wheat1]"
                    else:
                        pkey = f"[light_coral]{key}[][/light_coral]"

                    items = []
                    if isinstance(parsed.get(key), list):
                        items = parsed.get(key, [])
                    elif isinstance(parsed.get(key), dict):
                        items = [parsed.get(key, [])]
                    for nb, msg_parsed in enumerate(items):
                        new_pretty_chain = f"{pretty_chain+',' if pretty_chain else ''}{pkey},[navajo_white1]i{nb+1}[/navajo_white1]"
                        new_key_chain = f"{key_chain+',' if key_chain else ''}{skey}"
                        _pretty_print(sub['message_typedef'], msg_parsed, new_key_chain, new_pretty_chain)
                else:
                    new_pretty_chain = f"{pretty_chain+',' if pretty_chain else ''}{pkey}"
                    new_key_chain = f"{key_chain+',' if key_chain else ''}{skey}"

                    if sub["type"] == "message" and not sub.get("seen_repeated"):
                        _pretty_print(sub['message_typedef'], parsed.get(key, {}), new_key_chain, new_pretty_chain)
                    else:
                        type_name = sub["type"]
                        if key in parsed:
                            val = parsed[key]
                            if type(val) == str:
                                val = f'[spring_green3]"{val}"[/spring_green3]'
                            elif type(val) in [int, float]:
                                val = f'[steel_blue1]{val}[/steel_blue1]'
                            else:
                                val = str(val)
                        else:
                            if hide_empty:
                                return
                            val = "[bright_black][italic]empty[/italic][/bright_black]"

                        out_line = f"[light_cyan1]{('['+str(new_key_chain.count(',')+1)+']').ljust(4)}[/light_cyan1] {new_pretty_chain} -> <[magenta3]{type_name}[/magenta3]> = {val} [italic][{new_key_chain}][/italic]"
                        
                        raw_line = strip_markups(out_line)
                        raw_key_chain = strip_markups(new_key_chain)
                        raw_pretty_chain = strip_markups(new_pretty_chain)
                        raw_val = strip_markups(val)
                        
                        matched = not any([match_any, match_keychain, match_value])
                        if match_any:
                            for m in match_any:
                                if fnmatch(raw_line, m):
                                    matched = True
                        if match_keychain:
                            for m in match_keychain:
                                if fnmatch(raw_key_chain, m) or fnmatch(raw_pretty_chain, m):
                                    matched = True
                        if match_value:
                            for m in match_value:
                                if fnmatch(raw_val, m):
                                    matched = True
                        if matched:
                            if filter_any:
                                for m in filter_any:
                                    if fnmatch(raw_line, m):
                                        matched = False
                            if filter_keychain:
                                for m in filter_keychain:
                                    if (fnmatch(raw_key_chain, m) or fnmatch(raw_pretty_chain, m)):
                                        matched = False
                            if filter_value:
                                for m in filter_value:
                                    if fnmatch(raw_val, m):
                                        matched = False
                        if matched or not any([match_any, match_keychain, match_value, filter_any, filter_keychain, filter_value]):
                            cs.print(out_line)


        cs = Console(highlight=False)
        _pretty_print(self.schema, self.values)

def guess_schema(data: bytes, definitions: dict={}, bruteforce_index=20, no_autodetect=False) -> ProtoDeepSchema:
    if not no_autodetect:
        if data.strip().startswith(b"HTTP") and b"\r\n\r\n" in data:
            print("[!] Full request detected, extracting the body...")
            data = data.split(b"\r\n\r\n", 1)[1]

    schema, data_index = find_proto_schema(data, bruteforce_index)
    parsed = schema[0]
    new_schema = schema[1]

    new_schema, custom_types_defined = clean_schema(new_schema, parsed, definitions=definitions)
    if custom_types_defined:
        schema = decode_message(data[data_index:], new_schema)
        parsed = schema[0]
        new_schema = schema[1]
        new_schema, _ = clean_schema(new_schema, parsed, definitions=definitions)

    protodeep_schema = ProtoDeepSchema(schema=new_schema, values=parsed)
    return protodeep_schema