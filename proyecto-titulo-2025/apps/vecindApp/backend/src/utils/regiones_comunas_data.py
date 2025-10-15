"""
Utilidad para cargar y validar regiones y comunas desde el JSON estático.

Este módulo proporciona funciones para trabajar con el JSON de regiones y comunas
de Chile, permitiendo validar combinaciones de región-comuna sin necesidad de
consultar la base de datos.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ruta al archivo JSON
JSON_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "apps" / "vecindApp" / "frontend" / "public" / "data" / "regiones-comunas.json"

# Cache para no leer el archivo cada vez
_regiones_comunas_cache: Optional[Dict[str, List[str]]] = None


def load_regiones_comunas() -> Dict[str, List[str]]:
    """
    Carga el JSON de regiones y comunas desde el archivo.
    
    Returns:
        Dict con regiones como keys y listas de comunas como values
    """
    global _regiones_comunas_cache
    
    if _regiones_comunas_cache is not None:
        return _regiones_comunas_cache
    
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            _regiones_comunas_cache = json.load(f)
        return _regiones_comunas_cache
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {JSON_FILE_PATH}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al decodificar el JSON: {str(e)}")


def get_regiones() -> List[str]:
    """
    Obtiene la lista de todas las regiones.
    
    Returns:
        Lista con nombres de regiones
    """
    data = load_regiones_comunas()
    return list(data.keys())


def get_comunas_by_region(region_nombre: str) -> List[str]:
    """
    Obtiene las comunas de una región específica.
    
    Args:
        region_nombre: Nombre de la región
        
    Returns:
        Lista de comunas de la región
        
    Raises:
        ValueError: Si la región no existe
    """
    data = load_regiones_comunas()
    
    # Buscar primero con el nombre exacto
    if region_nombre in data:
        return data[region_nombre]
    
    # Si no existe, intentar buscar eliminando prefijos comunes
    region_normalizada = region_nombre.replace("Región ", "").replace("Región de ", "").strip()
    
    # Buscar con el nombre normalizado
    if region_normalizada in data:
        return data[region_normalizada]
    
    # Buscar de forma insensible a mayúsculas/minúsculas
    for key in data.keys():
        if key.lower() == region_nombre.lower() or key.lower() == region_normalizada.lower():
            return data[key]
    
    raise ValueError(f"La región '{region_nombre}' no existe")


def validate_region_comuna(region_nombre: str, comuna_nombre: str) -> bool:
    """
    Valida que una comuna pertenezca a una región específica.
    
    Args:
        region_nombre: Nombre de la región
        comuna_nombre: Nombre de la comuna
        
    Returns:
        True si la comuna pertenece a la región, False en caso contrario
    """
    try:
        comunas = get_comunas_by_region(region_nombre)
        # Comparación insensible a mayúsculas/minúsculas
        comunas_lower = [c.lower() for c in comunas]
        return comuna_nombre.lower() in comunas_lower
    except ValueError:
        return False


def find_region_by_comuna(comuna_nombre: str) -> Optional[str]:
    """
    Encuentra la región a la que pertenece una comuna.
    
    Args:
        comuna_nombre: Nombre de la comuna
        
    Returns:
        Nombre de la región o None si no se encuentra
    """
    data = load_regiones_comunas()
    
    for region, comunas in data.items():
        if comuna_nombre in comunas:
            return region
    
    return None


def get_all_comunas() -> List[str]:
    """
    Obtiene todas las comunas de todas las regiones.
    
    Returns:
        Lista con todas las comunas
    """
    data = load_regiones_comunas()
    all_comunas = []
    
    for comunas in data.values():
        all_comunas.extend(comunas)
    
    return all_comunas


def get_regiones_comunas_structure() -> List[Dict[str, any]]:
    """
    Obtiene la estructura completa de regiones y comunas para el frontend.
    
    Returns:
        Lista de diccionarios con estructura: [{"region": "...", "comunas": [...]}, ...]
    """
    data = load_regiones_comunas()
    
    result = []
    for region, comunas in data.items():
        result.append({
            "region": region,
            "comunas": comunas
        })
    
    return result

