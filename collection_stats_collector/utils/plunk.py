

def plunk(struct, recursive=True):
    structure_types = (dict, list)
    if not isinstance(struct, structure_types):
        raise NotImplementedError(
            f"Plunked structure should be a dict or a list, got {type(struct)}."
        )
    if isinstance(struct, dict):
        for k, v in dict(struct).items():
            if not v:
                del struct[k]
            elif recursive and isinstance(v, structure_types):
                plunk(v, recursive=recursive)
    elif isinstance(struct, list):
        for n, i in enumerate(reversed(list(struct))):
            if not i:
                del struct[len(struct)-1-n]
            elif recursive and isinstance(i, structure_types):
                plunk(i, recursive=recursive)
    return struct
