import socket
import struct
import time
import pyarrow as pa
import pandas as pd
import pickle

from typing import Tuple, Optional, Any
from threading import Lock

from .exceptions import InvalidDataType, InvalidDataType, InvalidQuery, \
    InvalidArrowData, InvalidPickleData, ProtocolVersionError, ConnectionError


class Serializer:

    def _process_set_data(self, response_type: str, payload: bytes) -> bool:
        if response_type == 'OK':
            return True
        if response_type == 'NA':
            return False
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 1:
            raise ValueError()
        raise self._general_handle_error_code(error_code)

    def _process_incr(self, response_type: str, payload: bytes) -> int:
        if response_type == 'IN':
            data = struct.unpack('>q', payload)[0]
            return data
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 5:
            raise InvalidDataType()
        raise self._general_handle_error_code(error_code)

    def _process_incr_float(self, response_type: str, payload: bytes) -> float:
        if response_type == 'FL':
            data = struct.unpack('>d', payload)[0]
            return data
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 5:
            raise InvalidDataType()
        raise self._general_handle_error_code(error_code)

    def _process_delete(self, response_type: str, payload: bytes) -> bool:
        if response_type == 'OK':
            return True
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 2:
            return False
        raise self._general_handle_error_code(error_code)

    def _process_delete_many(self, response_type: str, payload: bytes) -> int:
        if response_type == 'DM':
            deleted_count = struct.unpack('>H', payload)[0]
            return deleted_count
        error_code = struct.unpack('>H', payload)[0]
        raise self._general_handle_error_code(error_code)

    def _process_touch_response(self, response_type: str, payload: bytes) -> bool:
        if response_type == 'OK':
            return True
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 2:
            return False
        raise self._general_handle_error_code(error_code)

    def _process_ttl_response(self, response_type: str, payload: bytes) -> Optional[float]:
        if response_type == 'TL':
            ttl = struct.unpack('>Q', payload)[0]
            return ttl / 1000
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 2:
            return None
        raise self._general_handle_error_code(error_code)

    def _process_has_key_response(self, response_type: str, payload: bytes) -> bool:
        if response_type == 'OK':
            has_key = struct.unpack('?', payload)[0]
            return has_key
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        raise self._general_handle_error_code(error_code)

    def _process_keys_response(self, response_type: str, payload: bytes) -> list:
        if response_type == 'KY':
            if len(payload) == 0:
                return []
            return [key.decode() for key in payload.split(b'\x00')]
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        raise self._general_handle_error_code(error_code)

    def _process_flush_response(self, response_type: str, payload: bytes):
        if response_type == 'FU':
            return
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        raise self._general_handle_error_code(error_code)

    def _process_get_dataframe_response(self, response_type: str,
                                        payload: bytes) -> Optional[pd.DataFrame]:
        if response_type == 'AR':
            return self._process_arrow_payload(payload=payload)
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 2:
            return None
        if error_code == 3:
            raise InvalidQuery()
        if error_code == 4:
            raise InvalidArrowData()
        raise self._general_handle_error_code(error_code)

    def _process_get_response(self, response_type: str, payload: bytes, default: Optional[Any]) -> Any:
        if response_type == 'AR':
            return self._process_arrow_payload(payload=payload)
        if response_type == 'IN':
            data = struct.unpack('>q', payload)[0]
            return data
        if response_type == 'FL':
            data = struct.unpack('>d', payload)[0]
            return data
        if response_type == 'BY':
            try:
                return pickle.loads(payload)
            except pickle.UnpicklingError:
                raise InvalidPickleData()
        assert response_type == 'ER'
        error_code = struct.unpack('>H', payload)[0]
        if error_code == 2:
            if default is not None:
                return default
            return None
        if error_code == 5:
            raise InvalidDataType()
        raise self._general_handle_error_code(error_code)

    def _process_arrow_payload(self, payload: bytes,
                               metadata: Optional[dict] = None) -> pd.DataFrame:
        buffer_reader = pa.BufferReader(memoryview(payload))
        reader = pa.ipc.RecordBatchStreamReader(buffer_reader, options=None)
        dfs = []
        for record_batch in reader:
            if metadata:
                record_batch = record_batch.replace_schema_metadata(metadata)
            dfs.append(record_batch.to_pandas())
        return pd.concat(dfs)

    def _general_handle_error_code(self, error_code):
        if error_code == 6:
            return ProtocolVersionError('Please check the client version and the server version')
        return ValueError('Unknown error')


class SyncConnection:

    def __init__(
        self,
        host: str,
        port: int,
        kb_chunk: int = 64,
        socket_no_delay: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.protocol_version = 'B'.encode()
        self.host = host
        self.port = port
        self.lock = Lock()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if socket_no_delay:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.sock = sock
        self.chunk_size = 1024 * kb_chunk
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connect()

    def connect(self):
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < self.max_retries:
            try:
                self.sock.connect((self.host, self.port))
                return
            except socket.error as e:
                last_error = e
                attempts += 1
                if attempts < self.max_retries:
                    time.sleep(self.retry_delay)

        raise ConnectionError(f"Failed to connect after {self.max_retries} attempts") from last_error

    def close(self):
        self.sock.close()

    def send_command(self, message_type: str, payload: bytes) -> Tuple[str, bytes]:
        payload_length = len(payload)
        payload_length_bytes = struct.pack('>Q', payload_length)
        packet_bytes = self.protocol_version + message_type.encode() + payload_length_bytes

        with self.lock:
            self.sock.sendall(packet_bytes)
            self.sock.sendall(payload)

            header_length = 11
            response_header = bytearray()
            while header_length > 0:
                bytes_received = self.sock.recv(header_length)
                response_header.extend(bytes_received)
                header_length -= len(bytes_received)
            header = response_header[0:3].decode()
            if header[0] != 'B':
                raise ValueError('Wrong protocol')

            payload_len = struct.unpack('>Q', response_header[3:11])[0]
            response_payload = bytearray()
            while payload_len > 0:
                bytes_received = self.sock.recv(min(payload_len, self.chunk_size))
                response_payload.extend(bytes_received)
                payload_len -= len(bytes_received)
        return header[1:3], response_payload
