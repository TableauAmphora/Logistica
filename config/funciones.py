

def get_empresa_from_fuente(fuente): 
    if 'interandina' in fuente.lower():
        return 1
    elif 'retailsud' in fuente.lower():
        return 2
    else:
        return None