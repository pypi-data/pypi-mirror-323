from wexample_helpers_yaml.helpers.yaml_helpers import yaml_read_dict


def debug_handle_app_error(
    e: Exception,
    debug_config_file_name: str = '.env.yml'):
    from wexample_helpers.helpers.error import error_format
    import os

    # Load debug configuration from YAML
    debug_config = yaml_read_dict(
        os.path.join(os.getcwd(), debug_config_file_name)
    )

    error_format(
        error=e,
        paths_map=debug_config.get('host_paths_map', {})
    )
