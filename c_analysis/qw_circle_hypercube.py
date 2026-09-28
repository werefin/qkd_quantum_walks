# Shim: canonical implementation lives in the qkd_qw package (pip install -e .)
from qkd_qw.walks import QW_Circle, QW_Hypercube

__all__ = ["QW_Circle", "QW_Hypercube"]
