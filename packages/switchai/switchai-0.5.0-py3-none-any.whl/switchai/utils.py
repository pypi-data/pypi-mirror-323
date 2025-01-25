import base64
import io
import re
from typing import Any, Union

import PIL
from PIL.Image import Image


def encode_image(image_input: Union[str, bytes, Image]) -> str:
    """
    Encodes an image into a base64 string with PNG encoding.

    Args:
        image_input (Union[str, bytes, Image.Image]): The image to encode. Can be a file path (str),
        raw image bytes (bytes), or a PIL Image object.

    Returns:
        str: Base64-encoded PNG image string.
    """
    if isinstance(image_input, Image):
        image = image_input
    elif isinstance(image_input, bytes):
        image = PIL.Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, str):
        with open(image_input, "rb") as image_file:
            image = PIL.Image.open(image_file)
    else:
        raise TypeError("Unsupported input type. Must be str (file path), bytes, or PIL.Image.Image.")

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    png_bytes = buffered.getvalue()
    return base64.b64encode(png_bytes).decode("utf-8")


def is_url(path: str) -> bool:
    url_pattern = re.compile(r"^[a-zA-Z][a-zA-Z\d+\-.]*://")
    return bool(url_pattern.match(path))


def contains_image(inputs: Any) -> bool:
    if isinstance(inputs, list):
        return any(isinstance(item, Image) for item in inputs)
    return isinstance(inputs, Image)


def inline_defs(schema):
    if "$defs" in schema:
        defs = schema.pop("$defs")
        resolved = set()

        while True:
            remaining_refs = False

            for key, value in defs.items():
                ref_path = f"#/$defs/{key}"
                if ref_path not in resolved:
                    replace_refs(schema, ref_path, value)
                    replace_refs(defs, ref_path, value)
                    resolved.add(ref_path)
                    remaining_refs = True

            if not remaining_refs:
                break

    return schema


def replace_refs(obj, ref_path, definition):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if key == "$ref" and value == ref_path:
                obj.clear()
                obj.update(definition)
            else:
                replace_refs(value, ref_path, definition)
    elif isinstance(obj, list):
        for item in obj:
            replace_refs(item, ref_path, definition)
