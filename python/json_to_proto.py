# Read SWiG parameter list JSON file and create matching .proto file
import json

proto_contents = """
syntax = "proto3";
package subseawireless;
option java_package = "com.subseawireless.parameters";

message Parameter{
  enum identifier{
    INVALID = 0;
"""
# proto3 requires enums to start at zero, but zero is not used as an ID for this standard

with open('parameters.json') as json_file:
    params = json.load(json_file)["all"]

for param in params:
    proto_contents += f'    {param["name"]} = {param["id"]};\n'

proto_contents += """  }
  identifier id = 1;
  bool boolean = 2;
  int32 integer = 3;
  string string = 32;
}

message Message{
  int32 source = 1;
  int32 target = 2;
  repeated int32 requests = 3;  // List of parameter IDs requested
  repeated Parameter parameters = 4; // List of parameters sent
  repeated Parameter responses = 5; // List of parameters sent as response
}
"""

proto_file = open("parameters.proto", "w")
proto_file.write(proto_contents)
proto_file.close()

print("Done - remember to recompile using protoc!")
