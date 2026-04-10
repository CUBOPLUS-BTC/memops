"""Backend adapters and contracts for MemOps."""

from .contracts import (
    BackendError,
    BackendFeeRecommendations,
    BackendTransaction,
    BackendTransactionSummary,
    FeeEvidenceCompleteness,
    FeeEvidenceSource,
    TransactionBackend,
    TransactionFeeEvidence,
    TransactionNotFoundError,
    build_transaction_fee_evidence,
    normalize_raw_hex,
    normalize_txid,
)
from .mempool import MempoolSpaceBackend, build_mempool_api_base_url

__all__ = [
    "BackendError",
    "BackendFeeRecommendations",
    "BackendTransaction",
    "BackendTransactionSummary",
    "FeeEvidenceCompleteness",
    "FeeEvidenceSource",
    "MempoolSpaceBackend",
    "TransactionBackend",
    "TransactionFeeEvidence",
    "TransactionNotFoundError",
    "build_mempool_api_base_url",
    "build_transaction_fee_evidence",
    "normalize_raw_hex",
    "normalize_txid",
]
