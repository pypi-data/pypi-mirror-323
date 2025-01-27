from orin3_remote_engine_client.v1.error import RemoteEngineClientError

def validate_response(src):
    if src.common.result_code != 0:
        raise RemoteEngineClientError(src.common.result_code, src.common.detail)