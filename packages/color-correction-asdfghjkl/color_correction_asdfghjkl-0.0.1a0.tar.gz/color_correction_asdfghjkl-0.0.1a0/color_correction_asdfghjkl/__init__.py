__version__ = "0.0.1-alpha"


from .constant.color_checker import (
    reference_color_d50 as REFERENCE_COLOR_D50,  # noqa: N812
)
from .core.card_detection.yolov8_det_onnx import (
    YOLOv8CardDetector,
)
from .schemas.yolov8_det import (
    DetectionResult as YOLOv8DetectionResult,
)
from .services.color_correction import ColorCorrection

__all__ = [
    "__version__",
    "REFERENCE_COLOR_D50",
    "ColorCorrection",
    "YOLOv8CardDetector",
    "YOLOv8DetectionResult",
    "utils",
]
