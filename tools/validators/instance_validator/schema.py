from strictyaml import Map, MapPattern, Str, Optional, YAMLValidationError, Any, load, Enum, Regex, Seq
import sys
import os

# DEPRECATED
def get_ontology_file_list():
    ontology_fp = os.path.abspath('../../../ontology/yaml/resources/')
    yaml_files = []

    for root, _, files in os.walk(ontology_fp):
        for f in files:
            if f.endswith('.yaml'):
                yaml_files.append(os.path.join(root, f))
    
    return yaml_files

def build_universe():
    # add universe building packages to path
    sys.path.append(os.path.abspath(os.path.join('..', 'ontology_validator'))) 
    # add ontology files to path
    sys.path.append(os.path.abspath(os.path.join('../../../', 'ontology')))

    from yamlformat.validator import external_file_lib
    from yamlformat.validator import namespace_validator
    from yamlformat.validator import presubmit_validate_types_lib

    yaml_files = external_file_lib._RecursiveDirWalk('../../../ontology/yaml/resources/')
    config = presubmit_validate_types_lib.SeparateConfigFiles(yaml_files)
    universe = presubmit_validate_types_lib.BuildUniverse(config)

    entities = universe.entity_type_universe
    fields = universe.field_universe
    subfields = universe.subfield_universe
    states = universe.state_universe
    units = universe.unit_universe

    print(entities, fields, subfields, states, units)

# TODO check all valid states and ontological references in next validation steps
schema = MapPattern(Str(), 
    Map({
        'type': Str(), 
        'id': Str(), 
        Optional('connections'): MapPattern(Str(), Str())
                               | Seq(MapPattern(Str(), Str())),
        Optional('links'): MapPattern(Str(), 
            MapPattern(Str(), Str())),
        Optional('translation'): Any(),
        Optional('metadata'): Any()
    }))

translation_schema = Str() | Any()

# TODO add manual check for translation_data_schema to de-duplicate units/unit_values/states
# TODO add all units/unit_values/states to translation_data_schema
translation_data_schema = Str() | Map({
                                    'present_value': Str(),
                                    Optional('states'): MapPattern(Str(), Str()),
                                    Optional('units'): Map({
                                        'key': Str(),
                                        'values': MapPattern(Str(), Str())
                                    }),
                                    Optional('unit_values'): MapPattern(Str(), Str())
                                })

def load_yaml_with_schema(filepath, schema):
    f = open(filepath).read()

    try:
        parsed = load(f, schema)
        return parsed
    except YAMLValidationError as error:
        raise error

def main(filename):
    yaml = load_yaml_with_schema(filename, schema)

    top_name = yaml.keys()[0]

    if 'translation' in yaml[top_name].keys():
        translation = yaml[top_name]['translation']
        translation.revalidate(translation_schema)

        # TODO can this be automatically verified based on ontology?
        # if translation is not UDMI compliant
        if translation.data != 'COMPLIANT':
            translation_keys = translation.keys()

            for k in translation_keys:
                translation[k].revalidate(translation_data_schema)

    return yaml

'''
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: python3 schema.py yaml_file_path')
        sys.exit(1)

    filename = sys.argv[1]
    yaml = main(filename)

    print(yaml.as_yaml())
'''

build_universe()