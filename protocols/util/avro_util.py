
def handle_avro_errors(avro_output):
    """
    Parse the output of `protocol.validate_parts` displaying only the fields that have the value
    `False`
    -------
    Example
    -------
    {
        'problem': False,
        'not_a_problem': True,
        'nested': {
            'problem': False,
            'not_a_problem': True
        },
        'nested_twice': {
            'problem': {
                'big': False
            }
        },
        'nested_list': [
            {'problem': False, 'not_a_problem': True},
            {'no_problems': True},
            {'problems': False}
        ],
    }
    Returns
    {
        'nested': {'problem': 'Avro validation error'},
        'nested_list': {
            0: {'problem': 'Avro validation error'},
            2: {'problems': 'Avro validation error'}
        },
        'nested_twice': {
            'problem': {
                'big': 'Avro validation error'
            }
        },
        'problem': 'Avro validation error'
    }
    """
    if isinstance(avro_output, bool):
        if avro_output is False:
            return 'Avro validation error'
        return None
    if isinstance(avro_output, dict):
        result = {}
        for key, value in avro_output.items():
            handled_value = handle_avro_errors(value)
            if handled_value:
                result[key] = handled_value
        return result
    if isinstance(avro_output, list):
        result = {}
        for i, value in enumerate(avro_output):
            handled_value = handle_avro_errors(value)
            if handled_value:
                result[i] = handled_value
        return result
    raise TypeError('Cannot process "%s"' % type(avro_output))
