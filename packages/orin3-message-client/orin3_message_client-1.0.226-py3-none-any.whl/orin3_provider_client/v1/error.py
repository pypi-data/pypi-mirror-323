class ProviderClientError(Exception):
    def __init__(self, result_code: int = 0x1FFFFFFF, detail: str = ""):
        self.__result_code = result_code
        self.__detail = detail

    def __str__(self):
        return f"""ProviderClientError:
        result_code = {self.result_code}
        detail = \"{self.detail}\""""

    def __repr__(self):
        return f"ProviderClientError({self.result_code}:{self.detail})"

    @property
    def result_code(self) -> int:
        return self.__result_code
    
    @property
    def detail(self) -> str:
        return self.__detail