from protodeep.blackboxprotobuf import decode_message

from copy import deepcopy


def find_proto_schema(body: bytes, bruteforce_index: int=20):
    print("Finding the protobuf starting chunk...")
    
    output = None
    for i in range(bruteforce_index+1):
        try:
            output = decode_message(body[i:])
            print(f"[+] Bruteforce index : {i}\n")
            break
        except Exception:
            pass
    return output, i

def clean_schema(schema, parsed, definitions={}, named_keychains=False) -> tuple[dict[str], bool]:
    global custom_types_defined
    
    custom_types_defined = False

    def _clean_schema(message: dict, parsed: dict, key_chain: str="", defs: dict={}, named_keychains=False):
        global custom_types_defined

        original_message = deepcopy(message)
        for key, sub in original_message.items():
            skey = str(key)
            new_key_chain = f"{key_chain},{skey}" if key_chain else skey

            if new_key_chain in defs:
                if ":" in (def_val := defs[new_key_chain]):
                    custom_types_defined = True
                    sub["type"] = def_val.split(":")[-1]
                    def_val = def_val.split(":")[0]
                sub["name"] = def_val
            elif sub.get("name"):
                sub["name"] = ""

            if "alt_typedefs" in sub:
                del(sub["alt_typedefs"])
            if "example_value_ignored" in sub:
                sub["value"] = sub.pop("example_value_ignored")
            if "field_order" in sub:
                del(sub["field_order"])
            if "message_typedef" in sub:
                if isinstance(parsed, dict):
                    if skey in parsed:
                        sparsed = parsed[skey]
                        if isinstance(sparsed, list):
                            sub["seen_repeated"] = True # Repeated sub
                        sub["message_typedef"] = _clean_schema(sub["message_typedef"], sparsed, new_key_chain, defs, named_keychains)
                elif isinstance(parsed, list):
                    for item in parsed:
                        if skey in item:
                            sparsed = item[skey]
                            if isinstance(sparsed, list):
                                sub["seen_repeated"] = True # Repeated sub
                            sub["message_typedef"] = _clean_schema(sub["message_typedef"], sparsed, new_key_chain, defs, named_keychains)

            if named_keychains and not sub.get("message_typedef") and not sub.get("name"):
                del(message[key])
            else:
                message[key] = sub
        return message
    
    schema = _clean_schema(schema, parsed, defs=definitions, named_keychains=named_keychains)
    return schema, custom_types_defined