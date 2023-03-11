import json
from pathlib import Path

from protodeep.lib import guess_schema


def main(data: bytes=b"",
        proto_file: str="",
        defs_file: str="",
        definitions: dict={},
        hide_empty: bool=False,
        no_print: bool=False,
        data_type: str="",
        no_autodetect: bool=False,
        bruteforce_index: int=10,
        match_any: str="",
        match_keychain: str="",
        match_value: str="",
        filter_any: str="",
        filter_keychain: str="",
        filter_value: str="",
        export_protobuf: str="",
        export_protodeep: str="",
        compile: str="",
        stdin: bool=False,
        base64_input: bool=False,
        schema_name: str="Schema"
        ):
    
    # Args parsing

    if proto_file and stdin:
        exit("[-] You can't use a proto file and a stdin input at the same time. Please choose wisely. 🥹")

    if proto_file:
        with open(proto_file, "rb") as f:
            data = f.read()
    elif stdin:
        import sys, platform
        if platform.system() == "Windows":
            exit("[-] Piping bytes in terminal is fucked in Windows, please import your data from a file, or use Linux for this.")
        data = sys.stdin.buffer.read()
    else:
        exit("[-] Please choose at least a proto file or a stdin input. 🥶")

    if base64_input:
        import base64
        data = base64.b64decode(data)

    if defs_file:
        defs_path = Path(defs_file)
        if not defs_path.exists():
            exit(f"[-] Your definitions file \"{defs_file}\" doesn't exists. Are you lying to me ? 😔")
        if not defs_path.is_file():
            exit(f"[-] Bruh your definitions file is a folder. 😩")
        with open(defs_file, 'r', encoding="utf-8") as f:
            raw_defs = f.read()
        definitions = json.loads(raw_defs)

    # Main

    match data_type:
        case "protobuf":
            try:
                protodeep_schema = guess_schema(
                    data=data,
                    definitions=definitions,
                    bruteforce_index=bruteforce_index,
                    no_autodetect=no_autodetect
                )
            except:
                exit("[-] Can't decode the data. Please verify your type and bruteforce_index. Otherwise, RIP. 🥹")
        case "protodeep":
            import pickle
            from protodeep.lib import ProtoDeepSchema, clean_schema

            with open(proto_file, 'rb') as f:
                obj_data = pickle.load(f)
            protodeep_schema = ProtoDeepSchema(**obj_data)

            if definitions: # Applying definitions names (can't apply types because we need raw binary data)
                new_schema, _ = clean_schema(protodeep_schema.schema, protodeep_schema.values, definitions=definitions)
                protodeep_schema.schema = new_schema

        case _:
            exit('[-] Please make a choice between "protobuf" and "protodeep". You can do it. ❤️')

    if not no_print:
        protodeep_schema.pretty_print(
            hide_empty=hide_empty,
            match_any=match_any,
            match_keychain=match_keychain,
            match_value=match_value,
            filter_any=filter_any,
            filter_keychain=filter_keychain,
            filter_value=filter_value
        )

    # Export

    if export_protobuf:
        protodeep_schema.export_protofile(export_protobuf, schema_name)

    if export_protodeep:
        protodeep_schema.export_protodeep(export_protodeep)
        
    if compile:
        protodeep_schema.compile_python(compile, export_protobuf)