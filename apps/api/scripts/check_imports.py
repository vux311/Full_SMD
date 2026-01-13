import importlib
modules = [
    'src.infrastructure.databases',
    'src.api.routes',
    'src.create_app'
]

for m in modules:
    try:
        importlib.import_module(m)
        print(f'{m}: OK')
    except Exception as e:
        print(f'{m}: {type(e).__name__}: {e}')
