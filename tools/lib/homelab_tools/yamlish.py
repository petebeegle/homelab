"""YAML parsing helpers used by repo-local tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    values: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in values:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate field {key}",
                key_node.start_mark,
            )
        values[key] = loader.construct_object(value_node, deep=deep)
    return values


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def strip_quotes(value: str, *, quote_chars: str = "'\"") -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in quote_chars:
        return value[1:-1]
    return value


def parse_key_value_file(path: Path, *, quote_chars: str = '"') -> dict[str, str]:
    """Parse key=value files, preserving the harness marker error wording."""
    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{lineno}: expected key=value, got {raw_line!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = strip_quotes(value.strip(), quote_chars=quote_chars)
        if not key:
            raise ValueError(f"{path}:{lineno}: marker key must not be empty")
        values[key] = value
    return values


def parse_scalar_yaml_file(path: Path) -> dict[str, str]:
    """Parse a scalar-only key: value file."""
    data = _load_yaml_mapping(path)
    values: dict[str, str] = {}
    for key, value in data.items():
        field = _field_name(key, path)
        if isinstance(value, (dict, list)):
            raise ValueError(f"{path}: field {field} must be a scalar")
        values[field] = _scalar_text(value)
    return values


def parse_simple_yaml_file(path: Path) -> dict[str, object]:
    """Parse top-level scalars and two-space lists used by workflow plans."""
    data = _load_yaml_mapping(path)
    values: dict[str, object] = {}
    for key, value in data.items():
        field = _field_name(key, path)
        if value is None:
            values[field] = []
        elif isinstance(value, list):
            items: list[str] = []
            for item in value:
                if isinstance(item, (dict, list)):
                    raise ValueError(f"{path}: field {field} must be a list of scalars")
                text = _scalar_text(item)
                if not text:
                    raise ValueError(f"{path}: list item must not be empty")
                items.append(text)
            values[field] = items
        elif isinstance(value, dict):
            raise ValueError(f"{path}: field {field} must be a scalar or list")
        else:
            values[field] = _scalar_text(value)
    return values


def parse_frontmatter_text(
    text: str, *, strip_values: bool = False
) -> tuple[dict[str, Any], str, list[str]]:
    """Parse simple Markdown frontmatter and return metadata, body, and errors."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, text, ["missing opening frontmatter marker"]

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, text, ["missing closing frontmatter marker"]

    raw_frontmatter = "\n".join(lines[1:end])
    metadata, errors = _load_frontmatter(raw_frontmatter)
    if strip_values:
        metadata = _strip_metadata_values(metadata)
    return metadata, "\n".join(lines[end + 1 :]).strip(), errors


def parse_frontmatter_file(path: Path) -> tuple[dict[str, Any], list[str]]:
    """Parse simple Markdown frontmatter and return metadata plus parse errors."""
    metadata, _body, errors = parse_frontmatter_text(path.read_text(encoding="utf-8"))
    return metadata, errors


def parse_retrieval_manifest_file(path: Path, *, strict: bool = False) -> list[dict[str, object]]:
    """Parse the retrieval manifest subset shared by policy checks and context rendering."""
    data = _load_yaml_mapping(path)
    if strict:
        extra_keys = sorted(str(key) for key in data if key != "indexes")
        if extra_keys:
            raise ValueError(f"only indexes is supported at top level: {extra_keys}")

    raw_indexes = data.get("indexes", [])
    if raw_indexes is None:
        return []
    if not isinstance(raw_indexes, list):
        if strict:
            raise ValueError("indexes must be a list")
        return []

    indexes: list[dict[str, object]] = []
    for raw_index in raw_indexes:
        if not isinstance(raw_index, dict):
            if strict:
                raise ValueError("index item must be a mapping")
            continue
        index: dict[str, object] = {}
        for key, value in raw_index.items():
            field = str(key)
            if isinstance(value, list):
                index[field] = [
                    _scalar_text(item)
                    for item in value
                    if not isinstance(item, (dict, list))
                ]
            elif isinstance(value, (dict, list)):
                if strict:
                    raise ValueError(f"{field} must be a scalar or list")
            elif value is None:
                index[field] = []
            else:
                index[field] = _scalar_text(value)
        indexes.append(index)
    return indexes


def _load_yaml_mapping(path: Path) -> dict[Any, Any]:
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except ConstructorError as exc:
        raise ValueError(_yaml_error(exc)) from exc
    except yaml.YAMLError as exc:
        raise ValueError(_yaml_error(exc)) from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected top-level mapping")
    return data


def _load_frontmatter(text: str) -> tuple[dict[str, Any], list[str]]:
    try:
        data = yaml.load(text, Loader=_UniqueKeyLoader)
    except ConstructorError as exc:
        return {}, [_yaml_error(exc)]
    except yaml.YAMLError as exc:
        return {}, [_yaml_error(exc)]
    if data is None:
        return {}, []
    if not isinstance(data, dict):
        return {}, ["frontmatter must be a mapping"]
    return {str(key): _metadata_value(value) for key, value in data.items()}, []


def _field_name(key: object, path: Path) -> str:
    field = _scalar_text(key)
    if not field:
        raise ValueError(f"{path}: key must not be empty")
    return field


def _metadata_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_metadata_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _metadata_value(item) for key, item in value.items()}
    if value is None:
        return []
    return _scalar_text(value)


def _strip_metadata_values(metadata: dict[str, Any]) -> dict[str, Any]:
    return {key: _strip_metadata_value(value) for key, value in metadata.items()}


def _strip_metadata_value(value: Any) -> Any:
    if isinstance(value, str):
        return strip_quotes(value)
    if isinstance(value, list):
        return [_strip_metadata_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _strip_metadata_value(item) for key, item in value.items()}
    return value


def _scalar_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _yaml_error(error: yaml.YAMLError) -> str:
    problem = getattr(error, "problem", None)
    mark = getattr(error, "problem_mark", None)
    if problem and mark:
        return f"line {mark.line + 1}: {problem}"
    if problem:
        return str(problem)
    return str(error)
