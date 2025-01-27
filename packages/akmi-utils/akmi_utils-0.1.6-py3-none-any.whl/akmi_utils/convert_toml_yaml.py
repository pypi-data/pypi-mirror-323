import toml
import yaml

def convert_toml_to_yaml(input_toml_path, output_yaml_path):
    # Read the contents of the settings.toml file
    with open(input_toml_path, 'r') as toml_file:
        toml_content = toml.load(toml_file)

    # Convert the dictionary to a YAML formatted string
    yaml_content = yaml.dump(toml_content, default_flow_style=False)

    # Write the YAML string to a new file
    with open(output_yaml_path, 'w') as yaml_file:
        yaml_file.write(yaml_content)
