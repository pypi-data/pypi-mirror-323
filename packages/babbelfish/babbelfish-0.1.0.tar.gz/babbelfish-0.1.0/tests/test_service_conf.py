from dataclasses import dataclass

import heisskleber

import babbelfish


def test_create_from_dict() -> None:
    input_dict = {
        "name": "test",
        "output": {
            "mqtt": {
                "host": "mqtt.example.com",
                "port": 1883,
            },
            "zmq": {
                "host": "localhost",
                "port": 5555,
            },
        },
        "input": {"udp": {"host": "localhost", "port": 6969}},
    }

    test_conf = babbelfish.ServiceConf.from_dict(input_dict)

    assert isinstance(test_conf.senders["mqtt"], heisskleber.MqttSender)
    assert isinstance(test_conf.senders["zmq"], heisskleber.ZmqSender)
    assert isinstance(test_conf.receivers["udp"], heisskleber.UdpReceiver)


def test_create_receiver() -> None:
    input_dict = {
        "name": "test",
        "input": {"mqtt": {"host": "mqtt.example.com", "port": 1883, "user": "test", "topic": "test"}},
    }

    test_conf = babbelfish.ServiceConf.from_dict(input_dict)

    assert isinstance(test_conf.receivers["mqtt"], heisskleber.MqttReceiver)
    assert "test" in test_conf.receivers["mqtt"].topics
    assert "fischsuppe" not in test_conf.receivers["mqtt"].topics


def test_simple_inheritance() -> None:
    @dataclass
    class TestConf(babbelfish.ServiceConf):
        testing: bool = False

    input_dict = {
        "name": "test",
        "testing": True,
        "output": {
            "mqtt": {
                "host": "mqtt.example.com",
                "port": 1883,
            },
            "zmq": {
                "host": "localhost",
                "port": 5555,
            },
        },
        "input": {"udp": {"host": "localhost", "port": 6969}},
    }

    test_dict = TestConf.from_dict(input_dict)

    assert test_dict.testing is True
    assert isinstance(test_dict.senders["mqtt"], heisskleber.MqttSender)
    assert test_dict.senders["mqtt"].config.host == "mqtt.example.com"


def test_create_multiple_instances_of_same_type() -> None:
    input_dict = {
        "name": "test",
        "output": {
            "mqtt": {
                "host": "mqtt.example.com",
                "port": 1883,
            },
            "mqtt_2": {
                "host": "localhost",
                "port": 1883,
            },
        },
        "input": {"udp": {"host": "localhost", "port": 6969}, "udp_remote": {"host": "udp.example.com", "port": 7777}},
    }

    test_conf = babbelfish.ServiceConf.from_dict(input_dict)

    assert isinstance(test_conf.senders["mqtt"], heisskleber.MqttSender)
    assert isinstance(test_conf.senders["mqtt_2"], heisskleber.MqttSender)
    assert isinstance(test_conf.receivers["udp"], heisskleber.UdpReceiver)
    assert isinstance(test_conf.receivers["udp_remote"], heisskleber.UdpReceiver)
