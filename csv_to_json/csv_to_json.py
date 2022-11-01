# Read SWiG parameter list spreadsheet exported as CSV and create matching .json file
# Expects first line to be headers
import csv
import json
json_fields = ['id', 'description', 'name', 'access', 'optional', 'representation']

json_params = []
new_id = 129  # First ID to assign for undefined lines
with open('csv_to_json/parameters.csv', encoding='utf-8-sig') as csv_file:
  csv_params = csv.DictReader(csv_file, fieldnames=None, restkey=None, restval=None, dialect='excel')
  last_id = '0'
  for csv_param in csv_params:
    # print(csv_param)
    param = {}
    if len(csv_param['Id']) == 0:
      if len(csv_param['Description']) != 0:
        # print (f'After ID {last_id} - Assigning new ID {new_id} to line [{csv_param}]')
        param['id'] = f'{new_id}'
        new_id += 1
      else: # Assume blank line
        # print(f'After ID {last_id} Dropping line [{csv_param}]')
        continue
    else:
      param['id'] = csv_param['Id']
      last_id = param['id'] # Used in debug message above to locate missing IDs
    param_name = csv_param['Description'].replace(' ','_').lower()
    # print(f"{csv_param['Description']} - {param_name}")
    param['name'] = param_name
    param['description'] = csv_param['Description']
    
    # Read access permissions
    access = {}
    reads = csv_param['Read'].split('/')
    if len(reads) != 2: # Assume free read access by default where missing
      reads = ['F', 'F']

    writes = csv_param['Write'].split('/')
    if len(writes) != 2: # Assume no write access by default where missing
      reads = ['N', 'N']

    if reads[0] != 'N' and writes[0] != 'N':  # Some dry access is allowed
      access['dry'] = {}  # Create 'dry' section
      if reads[0] != 'N': # read is possible
        access['dry']['read'] = 'true'
      if reads[0] == 'A': # requires authentication
        access['dry']['read_auth'] = 'true'
      if reads[0] == 'O': # manufacturer option to implement
        access['dry']['read_option'] = 'true'
      if writes[0] != 'N': # write is possible
        access['dry']['write'] = 'true'
      if writes[0] == 'A': # requires authentication
        access['dry']['write_auth'] = 'true'
      if writes[0] == 'O': # manufacturer option to implement
        access['dry']['write_option'] = 'true'
      
    if reads[1] != 'N' and writes[1] != 'N':  # Some wet access is allowed
      access['wet'] = {}  # Create 'wet' section
      if reads[1] != 'N': # read is possible
        access['wet']['read'] = 'true'
      if reads[1] == 'A': # requires authentication
        access['wet']['read_auth'] = 'true'
      if reads[1] == 'O': # manufacturer option to implement
        access['wet']['read_option'] = 'true'
      if writes[1] != 'N': # write is possible
        access['wet']['write'] = 'true'
      if writes[1] == 'A': # requires authentication
        access['wet']['write_auth'] = 'true'
      if writes[1] == 'O': # manufacturer option to implement
        access['wet']['write_option'] = 'true'
      
      param['access'] = access

    if csv_param['Acoustic'] == 'N' or csv_param['Optical'] == 'N' or csv_param['Radio'] == 'N' or csv_param['Induction'] == 'N' or csv_param['Communications'] == 'N':
      optional = {}
      # print(param['id'], "Options: ", csv_param['Acoustic'], csv_param['Optical'], csv_param['Radio'], csv_param['Induction'], csv_param['Communications'])
      if csv_param['Acoustic'] == 'N':
        optional['acoustic'] = 'true'
      if csv_param['Optical'] == 'N':
        optional['optical'] = 'true'
      if csv_param['Radio'] == 'N':
        optional['radio'] = 'true'
      if csv_param['Induction'] == 'N':
        optional['inductive'] = 'true'
      if csv_param['Communications'] == 'N':  # Only required for power transfer
        optional['no_power'] = 'true'
        
      param['optional'] = optional

      if '1-bit' in csv_param['Representation'] or 'Bool' in csv_param['Representation']:
        param['representation'] = "boolean"
      elif '64' in csv_param['Representation']:
        param['representation'] = "uint64"
      elif '32' in csv_param['Representation']:
        param['representation'] = "uint32"
      elif '16' in csv_param['Representation']:
        param['representation'] = "uint16"
      elif '8' in csv_param['Representation'] or '100' in csv_param['Representation']:
        param['representation'] = "uint8"
      else: # Default to structured data represented in string
        param['representation'] = "json"

    json_params.append(param)
# Finished with source CSV file

# Process resulting JSON data from json_params back to CSV to compare with original
with open('csv_to_json/compare.csv', 'w', encoding='utf-8-sig') as csv_out:
  # Header line
  csv_fields = []
  for field in json_fields:
    if field == "access":
      csv_fields.append("Read, Write")
    elif field == "optional":
      csv_fields.append("Acoustic, Optical, Radio, Inductive, Communication")
    else:
      csv_fields.append(field)
  csv_line = (",".join(csv_fields))
  csv_out.writelines(csv_line + "\n")

  for param in json_params:
    csv_fields = []
    # print(param)
    for field in json_fields:
      if field == "access": # Extract access parameters in original spreadsheet format
        access = param.get(field,{})
        dry = access.get("dry",{})
        wet = access.get("wet",{})
        read = ""
        write = ""

        if dry.get("read_auth", False):
          read += "A"
        elif dry.get("read_option", False):
          read += "O"
        elif dry.get("read", False):
          read += "F"
        else:
          read += "N"
        read += "/"
        if wet.get("read_auth", False):
          read += "A"
        elif wet.get("read_option", False):
          read += "O"
        elif wet.get("read", False):
          read += "F"
        else:
          read += "N"

        if dry.get("write_auth", False):
          write += "A"
        elif dry.get("write_option", False):
          write += "O"
        elif dry.get("write", False):
          write += "F"
        else:
          write += "N"
        write += "/"
        if wet.get("write_auth", False):
          write += "A"
        elif wet.get("write_option", False):
          write += "O"
        elif wet.get("write", False):
          write += "F"
        else:
          write += "N"

        csv_fields.append(read)
        csv_fields.append(write)

      elif field == "optional":  # Extract exception columns
        options = param.get(field,{})
        for exception in ['acoustic', 'optical', 'radio', 'inductive', 'power']:
          if options.get(exception,'false') == 'true':  # If exception is offered for this technology
            csv_fields.append("N")
          else:
            csv_fields.append("")
      
      elif field in param:  # Generic fields
        if type(param[field]) is str:
          csv_fields.append(param[field])

      else:
        csv_fields.append("") # Default empty column if not included
        # print(f'Non-string {field} - {type(param.get(field,None))}- {param.get(field,"")}')

    if len(csv_fields) > 0:
      # print(csv_fields)
      csv_line = ",".join(csv_fields) + "\n"
      csv_out.writelines(csv_line)
#   print(param)
#     proto_contents += f'    {param["name"]} = {param["id"]};\n'

# proto_file = open("parameters.proto", "w")
# proto_file.write(proto_contents)
# proto_file.close()

# Convert data back to CSV for manual comparison