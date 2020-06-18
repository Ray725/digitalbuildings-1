from strictyaml import Map, MapPattern, Str, Optional, YAMLValidationError, Any, load, Enum, Regex, Seq
import sys


'''
demo:
- good_building
- bad_syntax
- bad_tabbing
- bad_dup_keys
- good_connections
- bad_connections
- good_translation*
- bad_translation*
- good_link
- bad_link

questions:
- for virtual entities, ID not required. so I think to check this in ontology, but where's a list of virtual types?
- i'm not sure how to parse metadata?
'''

schema = MapPattern(Str(), 
    Map({
        'type': Str(), 
        'id': Str(), 
        Optional('connections'): Seq(Str())
                                   | MapPattern(Str(), 
                                                Enum(['CONTAINS', 'CONTROLS', 'FEEDS', 'HAS_PART', 'HAS_RANGE'])),
        Optional('links'): MapPattern(Str(), 
            MapPattern(Str(), Str())),
        Optional('translation'): Any(),
        Optional('metadata'): Any()
    }))

translation_schema = Regex('COMPLIANT') | Any()

# TODO add manual check for translation_data_schema to de-duplicate units/unit_values/states
# TODO add all units/unit_values/states to translation_data_schema
translation_data_schema = Str() | Map({
                                    'present_value': Str(),
                                    Optional('states'): Map({
                                        Optional('ON'): Str(),
                                        Optional('OFF'): Str(),
                                        Optional('AUTO'): Str(),
                                        Optional('OPEN'): Str(),
                                        Optional('CLOSED'): Str(),
                                        Optional('LOW'): Str(),
                                        Optional('MEDIUM'): Str(),
                                        Optional('HIGH'): Str(),
                                        Optional('OCCUPIED'): Str(),
                                        Optional('UNOCCUPIED'): Str()
                                    }),
                                    Optional('units'): Map({
                                        'key': Str(),
                                        'values': Map({
                                            Optional('milliamperes'): Str(),
                                            Optional('kilowatt_hours'): Str(),
                                            Optional('degrees_celsius'): Str(),
                                            Optional('degrees_fahrenheit'): Str()
                                        })
                                    }),
                                    Optional('unit_values'): Map({
                                        Optional('milliamperes'): Str(),
                                        Optional('kilowatt_hours'): Str(),
                                        Optional('degrees_celsius'): Str(),
                                        Optional('degrees_fahrenheit'): Str()
                                    })
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