# Capability reporting
Options for a device to provide reference to its capability for a given parameter

## Introduction
A SWiG device needs to be able to report its capabilities, for a user to know acceptable range for parameters. This reporting will take place on the same interface as used to set/get parameters, so will be integrated in the same protocol

## Types of capability
- `min/max` - device provides two values representing the lowest and highest values which it can accept (useful for numeric types)
- `list` - device provides multiple values, listing all which are acceptable to the device (any data type)
- `regex` - device provides regex to validate a string (string type)
- `schema` - device provides schema to validate a json type (json type)
- `unlimited` - default, device accepts any value (any data type)
- `not implemented` (support for the parameter is not implemented). This may be provided in response to a known parameter which is optional but not implemented
- `unknown` (parameter is not recognised). This may be provided in response to an invalid parameter request

## Requesting capability
The protocol should provide a parallel route to request capability, with minimal difference from setting parameters, e.g. using the same parameter identifiers and data format (JSON, protobuf etc) to simplify implementation and provide a consistent user interface.

## Optional capability implementation
A SWiG device must gracefully fail if it can not report capability for any requested parameter (even those with identifiers which have not been defined, which should be reported as `unknown`)
Users of a SWiG device may request parameters values which are outwith the provided capability range. *TBD* how should the device respond to these

## TBD
- Should/May the device silently ignore parameter settings outwith capability range? Or should/must the device respond with an error state to unacceptable parameters
- How to handle linked/conditional parameters? The range of parameters for one value may depend on the current setting of another value. Should the reported capability be the full supported range or the currently available range?
  - Full supported range - easy to implement, doesn't change, but needs a way to reject an invalid combination of parameters when the user attempts to apply them.
  - Currently available range - useful feedback, needs to be based on the currently set values even if not applied, so a completed configuration can be built up, and the device will need to accept parameters outwith the currently available range as they may become valid when another parameter is changed.