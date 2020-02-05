message_downloader = {
    'type': 'object',
    'properties': {
        'configuration': {
            'type': 'string'
        },
        'expires': {
            'type': 'integer',
            'minimum': 0
        },
        'parent_url': {
            'type': 'string'
        },
        'stage': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        }
    },
    'required': [
        'configuration', 'expires', 'stage', 'url'
    ]
}

message_parser = {
    'type': 'object',
    'properties': {
        'cache_path': {
            'type': 'string'
        },
        'configuration': {
            'type': 'string'
        },
        'stage': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        }
    },
    'required': [
        'cache_path', 'configuration', 'stage'
    ]
}

message_indexer = {
    'type': 'object',
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'attributes': {
                    'type': 'object'
                },
                'configuration': {
                    'type': 'string'
                },
                'stage': {
                    'type': 'string'
                },
                'url': {
                    'type': 'string'
                }
            },
            'required': [
                'configuration', 'stage', 'url'
            ]
        },
        'index': {
            'type': 'string'
        }
    },
    'required': [
        'data', 'index'
    ]
}
