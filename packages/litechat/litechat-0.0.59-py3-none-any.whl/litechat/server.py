from ._llamacpp_oai_server import llamacpp_server
from ._core._api import litechat_server


def server(
    models_dir: str = None,
    host="0.0.0.0",
    port=None,
    log_level="info",
    animation=False,
    **model_kwargs
):
    if models_dir:
        port = 11438 if port is None else int(port)
        llamacpp_server(models_dir, host, port, **model_kwargs)
    else:
        port = 11437 if port is None else int(port)
        litechat_server(host, port, log_level, animation)
