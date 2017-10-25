# coding=utf-8

import argparse
import collections
from collections import OrderedDict
from lxml import etree
from path import Path

VERSION = r'1.0'

GAME_PATH = Path('E:\Program Files (x86)\Steam\steamapps\common\Divinity Original Sin 2')
SOD_PATH = Path('Data\Editor\Config\Stats\StatObjectDefinitions.sod')
OUTPUT_PATH = Path('out').abspath()

SOD_FILE_PATH_IN = Path.joinpath(GAME_PATH, SOD_PATH)
SOD_FILE_PATH_OUT = Path.joinpath(OUTPUT_PATH, SOD_PATH).abspath()


def main() -> None:
    if True not in [argv.runeslots_v1_patcher]:
        exit('No patches enabled.')

    if argv.runeslots_v1_patcher:
        field_definition_names = ['RuneSlots', 'RuneSlots_V1']

    root = etree.parse(SOD_FILE_PATH_IN, etree.XMLParser(remove_blank_text=True)).getroot()
    field_definitions = root.findall('stat_object_definitions/stat_object_definition/field_definitions')
    field_definitions_to_patch = [field_definition for field_definition in field_definitions
                                  if field_definition.find(f'field_definition[@name="{field_definition_names[0]}"]') is not None
                                  and field_definition.find(f'field_definition[@name="{field_definition_names[1]}"]') is None]

    if not field_definitions_to_patch:
        exit('Nothing to patch.')

    if argv.clean:
        OUTPUT_PATH.rmtree_p()

    SOD_FILE_PATH_OUT.dirname().makedirs_p()

    if argv.runeslots_v1_patcher:
        print('Running RuneSlots_V1 patcher:')
        # insert RuneSlots_V1 of type Integer after RuneSlots
        insert_definitions('RuneSlots_V1', 'Integer', 'RuneSlots', field_definitions_to_patch)

    SOD_FILE_PATH_OUT.write_text(etree.tostring(root, encoding='unicode', pretty_print=True), encoding='utf-8')
    print(f'Wrote patched stat object definitions to:\n\t{SOD_FILE_PATH_OUT}')


def insert_definitions(def_name: str, def_type: str, preceding_def_name: str, field_definitions_to_patch: collections.Iterable) -> None:
    for field_definitions in field_definitions_to_patch:
        preceding_field = field_definitions.find(f'field_definition[@name="{preceding_def_name}"]')

        field_def_data = OrderedDict({'index': '', 'name': def_name, 'display_name': def_name, 'export_name': def_name, 'type': def_type})
        field_def = etree.Element('field_definition', field_def_data)

        insert_position = field_definitions.index(preceding_field) + 1
        field_definitions.insert(insert_position, field_def)

        for i in range(insert_position, len(field_definitions)):
            field_definitions[i].set('index', str(i))

        print(f'\tPatched "{field_definitions.getparent().get("name")}" stat object definition.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--version', action='version', version=f'SOD Patcher v{VERSION} by fireundubh')
    parser.add_argument('--clean', action='store_true', dest='clean', default=True)
    parser.add_argument('--runeslots-v1-patch', action='store_true', dest='runeslots_v1_patcher', default=True)
    argv = parser.parse_args()
    main()
