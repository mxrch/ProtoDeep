These are test files from:
- https://github.com/protocolbuffers/protobuf/tree/main/src/google/protobuf/testdata

For each set of files with the same name:
* The file without extension is the original file
* .b64 is the same file, base64-encoded
* .hex is the same file, hex-encoded
* .protoc is the output of `protoc --decode_raw < file_without_extension` (for comparison)
* .txt is the output of ProtoDeep
