# drf-yasg 설정 추가
INSTALLED_APPS += [
    'drf_yasg',
]

# Swagger 설정
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'PERSIST_AUTH': True,
    'DEFAULT_MODEL_RENDERING': 'example',
} 