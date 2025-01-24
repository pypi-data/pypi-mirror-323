import logging
from pathlib import Path
from typing import Iterable, Optional, cast

from google.protobuf import text_format
from tokenizers import AddedToken

from briton.proto import AddedToken as AddedTokenProto
from briton.proto import AddedTokens, BritonConfig
from briton.trtllm_config import TrussTRTLLMBatchSchedulerPolicy


def trtllm_config_check(config):
    if "trt_llm" not in config:
        raise ValueError("trt_llm config is required for this model")


def batch_scheduler_policy_to_int(
    policy: TrussTRTLLMBatchSchedulerPolicy, logger: logging.Logger
) -> int:
    if policy == TrussTRTLLMBatchSchedulerPolicy.MAX_UTILIZATION:
        return 0
    elif policy == TrussTRTLLMBatchSchedulerPolicy.GUARANTEED_NO_EVICT:
        return 1
    else:
        logger.warning(f"Unknown batch scheduler policy: {policy}. Using GUARANTEED_NO_EVICT.")
        return 1


def create_briton_config_pbtxt(
    engine_path: str,
    hf_tokenizer: str,
    fsm_cache_dir: str,
    kv_cache_free_gpu_mem_fraction: float,
    port: int,
    added_tokens: list,
    max_num_tokens: Optional[int],
    config_pbtxt_path: Path,
    kv_cache_host_memory_bytes: Optional[int] = None,
    enable_kv_cache_reuse: bool = True,
    enable_chunked_context: bool = False,
    batch_scheduler_policy: Optional[int] = None,
):
    briton_config = BritonConfig(
        engine_path=engine_path,
        hf_tokenizer=hf_tokenizer,
        kv_cache_free_gpu_mem_fraction=kv_cache_free_gpu_mem_fraction,
        kv_cache_host_memory_bytes=kv_cache_host_memory_bytes,
        enable_kv_cache_reuse=enable_kv_cache_reuse,
        enable_chunked_context=enable_chunked_context,
        port=port,
        fsm_cache_dir=fsm_cache_dir,
        max_num_tokens=max_num_tokens,
        batch_scheduler_policy=batch_scheduler_policy,
        added_tokens=AddedTokens(
            tokens=[
                AddedTokenProto(
                    content=token.content,
                    single_word=token.single_word,
                    lstrip=token.lstrip,
                    rstrip=token.rstrip,
                    normalized=token.normalized,
                    special=token.special,
                )
                for token in cast(Iterable[AddedToken], added_tokens)
            ]
        ),
    )
    with open(config_pbtxt_path, "w") as f:
        f.write(text_format.MessageToString(briton_config))
