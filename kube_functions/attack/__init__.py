from kube_functions.attack.token_theft import steal_tokens, definition as token_def

definitions = [token_def]

def dispatch(name: str, args: dict, k8s=None, k8s_apps=None) -> str:
    if name == "steal_tokens":
        return steal_tokens(k8s, **args)
    return None