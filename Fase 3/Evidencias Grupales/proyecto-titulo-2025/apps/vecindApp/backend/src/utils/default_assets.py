"""
Utilidades para cargar assets por defecto del sistema.
"""

import os
import base64
from pathlib import Path
from typing import Optional


def get_assets_path() -> Path:
    """
    Obtiene la ruta absoluta al directorio de assets.

    Returns:
        Path: Ruta al directorio src/assets
    """
    # Obtener el directorio del archivo actual (src/utils/)
    current_dir = Path(__file__).parent
    # Subir un nivel para llegar a src/ y luego ir a assets/
    assets_dir = current_dir.parent / "assets"
    return assets_dir


def load_default_profile_image() -> Optional[bytes]:
    """
    Carga la imagen de perfil por defecto desde assets/images/avatar-placeholder2.svg

    Returns:
        bytes: Datos binarios de la imagen o None si no existe
    """
    try:
        assets_path = get_assets_path()
        image_path = assets_path / "images" / "avatar-placeholder2.svg"

        if image_path.exists():
            with open(image_path, "rb") as f:
                return f.read()
        else:
            # Si no existe el archivo, retornar una imagen muy pequeña por defecto
            return get_fallback_profile_image()
    except Exception:
        return get_fallback_profile_image()


def get_fallback_profile_image() -> bytes:
    """
    Imagen de respaldo muy pequeña (1x1 pixel) en caso de que no exista el archivo.

    Returns:
        bytes: Datos binarios de imagen JPEG mínima
    """
    # Imagen JPEG 1x1 pixel gris en base64
    tiny_jpeg_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA8="
    return base64.b64decode(tiny_jpeg_base64)


def load_default_profile_image_base64() -> str:
    """
    Carga la imagen de perfil por defecto y la convierte a base64.

    Returns:
        str: Imagen en formato "data:image/svg+xml;base64,..."
    """
    try:
        image_data = load_default_profile_image()
        if image_data:
            base64_data = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/svg+xml;base64,{base64_data}"
        return None
    except Exception:
        return None


def create_default_profile_image():
    """
    Verifica que existe la imagen de perfil por defecto avatar-placeholder2.svg
    """
    try:
        assets_path = get_assets_path()
        images_path = assets_path / "images"
        image_path = images_path / "avatar-placeholder2.svg"

        if image_path.exists():
            print(f"✅ Imagen por defecto encontrada: {image_path}")
            print("📁 Usando avatar-placeholder2.svg como imagen por defecto")
        else:
            print(f"❌ No se encontró avatar-placeholder2.svg en: {images_path}")
            print(
                "💡 Asegúrate de que el archivo avatar-placeholder2.svg esté en la carpeta assets/images/"
            )

    except Exception as e:
        print(f"❌ Error al verificar imagen por defecto: {e}")


if __name__ == "__main__":
    # Crear imagen por defecto si se ejecuta directamente
    create_default_profile_image()
