from orin3_provider_client.v1.error import ProviderClientError

def validate_response(src):
    if src.common.result_code != 0:
        raise ProviderClientError(src.common.result_code, src.common.detail)