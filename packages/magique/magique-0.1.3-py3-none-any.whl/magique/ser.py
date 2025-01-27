import abc

import msgpack
import cloudpickle


class Serializer(abc.ABC):
    @abc.abstractmethod
    def serialize(self, data: dict) -> bytes:
        pass

    @abc.abstractmethod
    def deserialize(self, data: bytes) -> dict:
        pass


class DefaultSerializer(Serializer):
    def serialize_pyobj(self, data: object) -> bytes:
        return cloudpickle.dumps(data)

    def deserialize_pyobj(self, data: bytes) -> object:
        return cloudpickle.loads(data)

    def serialize(self, data: dict) -> bytes:
        action = data.get("action")
        if action == "invoke_service":
            parameters = data["parameters"]
            ser_parameters = {}
            for key, value in parameters.items():
                ser_parameters[key] = self.serialize_pyobj(value)
            return msgpack.packb({**data, "parameters": ser_parameters})
        elif action == "worker_response":
            result = data.pop("result")
            ser_result = self.serialize_pyobj(result)
            return msgpack.packb({**data, "result": ser_result})
        return msgpack.packb(data)

    def deserialize(self, data: bytes) -> dict:
        res: dict = msgpack.unpackb(data)
        if not ("action" in res):
            return res
        action = res["action"]
        if action == "invoke_service":
            ser_parameters = res.pop("parameters")
            parameters = {}
            for key, value in ser_parameters.items():
                parameters[key] = self.deserialize_pyobj(value)
            res["parameters"] = parameters
        elif action == "worker_response":
            result = res.pop("result")
            ser_result = self.deserialize_pyobj(result)
            res["result"] = ser_result
        return res
