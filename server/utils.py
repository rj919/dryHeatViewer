__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def find_file(query_string, root_path):

    results_list = []

    return results_list

def ingest_environ():

    from os import environ
    typed_dict = {}
    environ_variables = dict(environ)
    for key, value in environ_variables.items():
        if value.lower() == 'true':
            typed_dict[key] = True
        elif value.lower() == 'false':
            typed_dict[key] = False
        elif value.lower() == 'null':
            typed_dict[key] = None
        elif value.lower() == 'none':
            typed_dict[key] = None
        else:
            try:
                try:
                    typed_dict[key] = int(value)
                except:
                    typed_dict[key] = float(value)
            except:
                typed_dict[key] = value

    return typed_dict

def load_settings(file_path, secret_key=''):

# validate inputs
    title = 'load_settings'
    try:
        _key_arg = '%s(file_path=%s)' % (title, str(file_path))
    except:
        raise ValueError('%s(file_path=...) must be a string.' % title)

# create extension parser
    from labpack.parsing.regex import labRegex
    file_extensions = {
            "json": ".+\\.json$",
            "json.gz": ".+\\.json\\.gz$",
            "yaml": ".+\\.ya?ml$",
            "yaml.gz": ".+\\.ya?ml\\.gz$",
            "drep": ".+\\.drep$"
        }
    ext_types = labRegex(file_extensions)

# retrieve file details
    key_map = ext_types.map(file_path)[0]
    if key_map['json']:
        import json
        try:
            file_data = open(file_path, 'rt')
            file_details = json.loads(file_data.read())
        except:
            raise ValueError('%s is not valid json data.' % _key_arg)
    elif key_map['yaml']:
        import yaml
        try:
            file_data = open(file_path, 'rt')
            file_details = yaml.load(file_data.read())
        except:
            raise ValueError('%s is not valid yaml data.' % _key_arg)
    elif key_map['json.gz']:
        import gzip
        import json
        try:
            file_data = gzip.open(file_path, 'rb')
        except:
            raise ValueError('%s is not valid gzip compressed data.' % _key_arg)
        try:
            file_details = json.loads(file_data.read().decode())
        except:
            raise ValueError('%s is not valid json data.' % _key_arg)
    elif key_map['yaml.gz']:
        import gzip
        import yaml
        try:
            file_data = gzip.open(file_path, 'rb')
        except:
            raise ValueError('%s is not valid gzip compressed data.' % _key_arg)
        try:
            file_details = yaml.load(file_data.read().decode())
        except:
            raise ValueError('%s is not valid yaml data.' % _key_arg)
    elif key_map['drep']:
        from labpack.compilers import drep
        try:
            file_data = open(file_path, 'rb').read()
            file_details = drep.load(encrypted_data=file_data, secret_key=secret_key)
        except:
            raise ValueError('%s is not valid drep data.' % _key_arg)
    else:
        ext_names = []
        ext_methods = set(ext_types.__dir__()) - set(ext_types.builtins)
        for method in ext_methods:
            ext_names.append(getattr(method, 'name'))
        raise ValueError('%s must be one of %s file types.' % (_key_arg, ext_names))

    return file_details

def retrieve_settings(model_path, file_path, secret_key=''):

# validate input
    title = 'retrieve_settings'
    from jsonmodel.validators import jsonModel
    model_details = load_settings(model_path)
    settings_model = jsonModel(model_details)

# try to load settings from file
    file_settings = {}
    try:
        file_settings = load_settings(file_path, secret_key)
    except:
        pass

# retrieve environmental variables
    environ_var = ingest_environ()

#  construct settings details from file and environment
    settings_details = settings_model.ingest(**{})
    for key in settings_model.schema.keys():
        if key.upper() in environ_var.keys():
            settings_details[key] = environ_var[key.upper()]
        elif key in file_settings.keys():
            settings_details[key] = file_settings[key]

    return settings_details

if __name__ == '__main__':
    import os
    os.environ['scheduler_job_store_pass'] = 'test_pass'
    settings = retrieve_settings('models/settings_model.json', '../notes/settings.yaml')
    assert settings['scheduler_job_defaults_coalesce']
    assert settings['scheduler_job_store_pass'] == 'test_pass'
    print(settings)