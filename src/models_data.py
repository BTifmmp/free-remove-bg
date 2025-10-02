
AVAILABLE_MODELS = [
    "rmbg14",
    "rmbg20"
]

MODELS_CONFIG = {
    "rmbg14": {
        "files": [
            "config.json", 
            "briarmbg.py", 
            "model.safetensors", 
            "MyConfig.py"
        ],
        'repoId': 'regitBT/rmbg14fork',
        'repoType': 'model'
    },
    "rmbg20": {
        "files": [
            "config.json", 
            "BiRefNet_config.py", 
            "model.safetensors", 
            "birefnet.py"
        ],
        'repoId': 'regitBT/rmbg20fork',
        'repoType': 'model'
    }
}