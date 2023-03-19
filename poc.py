from protodeep.lib import guess_schema
input_data = b'\x83\x01\x88\x01h\x84\x01\x92\x01\x02\x08i'
schema = guess_schema(data=input_data)
schema.pretty_print()