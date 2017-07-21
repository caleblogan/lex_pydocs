import argparse
import json

SLOTS_PATH = '../res/slots/'


def read_raw_vals(slot_raw_filename):
    """Reads the raw slot vals from slot_filename and returns them as a list"""
    raw_vals_list = []
    with open(SLOTS_PATH + slot_raw_filename, 'r') as fh:
        for val in fh.readlines():
            raw_vals_list.append(val.strip())
    return raw_vals_list


def generate_slot(slot_name, slot_description, slot_raw_filename):
    """Creates the slot in memory as a dict"""
    slot = {
        'enumerationValues': [],
        "name": slot_name,
        "description": slot_description
    }
    slot_raw_vals = read_raw_vals(slot_raw_filename)
    for slot_val in slot_raw_vals:
        slot['enumerationValues'].append({'value': slot_val})

    return slot


def save_slot(slot_dict, slot_name):
    """Writes the slot as a json file for uploading to lex-modules"""
    output_path = f'{SLOTS_PATH}{slot_name}.json'
    with open(output_path, 'w') as fh:
        fh.writelines(json.dumps(slot_dict))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates json slots file for uploading to lex-models from raw text')
    parser.add_argument('slot_name',
                        help='The name of your slot.')
    parser.add_argument('slot_description',
                        help='The description of your slot.')
    parser.add_argument('slot_raw_filename',
                        help='The filename of your raw slot vals.')

    args = parser.parse_args()

    generated_slot = generate_slot(args.slot_name, args.slot_description, args.slot_raw_filename)

    save_slot(generated_slot, args.slot_name)
