from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, TypeVar

import yaml  # type: ignore [import-untyped]
from heisskleber import Receiver, Sender
from heisskleber.core import _config_registry, _receiver_registry, _sender_registry

T = TypeVar("T", bound="ServiceConf")


@dataclass
class ServiceConf:
    """Baseclass for babbelfish service configurations."""

    name: str
    senders: dict[str, Sender[Any]] = field(default_factory=dict)
    receivers: dict[str, Receiver[Any]] = field(default_factory=dict)

    @classmethod
    def from_file(cls: type[T], file: str | Path) -> T:
        """Create a config object from a file path.

        Args:
            file: the file to load

        Note:
            Currently only supports .yaml extension.
        """
        path = Path(file)
        with path.open() as f:
            return cls.from_dict(dict(yaml.safe_load(f)))

    @classmethod
    def from_dict(cls: type[T], config_dict: dict[str, Any]) -> T:
        """Create a config from a dictionary.

        Filters out any unknown entries (without raising a warning, so check your spellingl)

        Args:
            config_dict: the dictionary that you want to turn into a dataclass.
        """
        sender_section = config_dict.pop("output", {})
        receiver_section = config_dict.pop("input", {})
        sender_instances = {}
        receiver_instances = {}

        for name, protocol_config in sender_section.items():
            protocol_name = name.split("_")[0]
            config_cls = _config_registry.get(protocol_name)
            sender_cls = _sender_registry.get(protocol_name)
            if config_cls and sender_cls:
                config_instance = config_cls.from_dict(protocol_config)
                sender_instances[name] = sender_cls(config_instance)  # type: ignore [call-arg]
            else:
                msg = f"Unknown protocol '{protocol_name}'"
                raise ValueError(msg)

        for name, protocol_config in receiver_section.items():
            protocol_name = name.split("_")[0]
            config_cls = _config_registry.get(protocol_name)
            receiver_cls = _receiver_registry.get(protocol_name)
            if config_cls and receiver_cls:
                kwargs = {"topic": protocol_config.pop("topic")} if "topic" in protocol_config else {}
                config_instance = config_cls.from_dict(protocol_config)
                receiver_instances[name] = receiver_cls(config_instance, **kwargs)  # type: ignore [call-arg]
            else:
                msg = f"Unknown protocol '{protocol_name}'"
                raise ValueError(msg)

        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        service_config = cls(**filtered_dict)
        service_config.senders = sender_instances
        service_config.receivers = receiver_instances
        return service_config
