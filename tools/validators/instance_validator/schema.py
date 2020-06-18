from strictyaml import Map, MapPattern, Str, Optional, YAMLValidationError, Any, load, Enum, Regex, Seq
import sys

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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: python3 schema.py yaml_file_path')
        sys.exit(1)

    filename = sys.argv[1]
    yaml = main(filename)

    print(yaml.as_yaml())