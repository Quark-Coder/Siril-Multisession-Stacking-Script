from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class CalibrationFrameType(Enum):
    BIAS = "bias"
    DARK = "dark"
    FLAT = "flat"


@dataclass
class CalibrationFrame:
    type: CalibrationFrameType
    file_path: Path
    exposure_time: Optional[float] = None
    temperature: Optional[float] = None
    gain: Optional[int] = None
    
    def is_valid(self) -> bool:
        """Проверяет валидность калибровочного кадра"""
        if not self.file_path.exists():
            return False
            
        if self.type in [CalibrationFrameType.DARK, CalibrationFrameType.FLAT]:
            return self.exposure_time is not None
            
        return True


class CalibrationFrameSet:
    def __init__(self, frame_type: CalibrationFrameType):
        self.frame_type = frame_type
        self.frames: list[CalibrationFrame] = []
        self._master_frame: Optional[Path] = None

    @property
    def master_frame(self) -> Optional[Path]:
        return self._master_frame

    @master_frame.setter 
    def master_frame(self, path: Path):
        if path.exists():
            self._master_frame = path
        else:
            raise FileNotFoundError(f"Master frame not found at {path}")

    def add_frame(self, frame: CalibrationFrame) -> None:
        """Добавляет калибровочный кадр в набор"""
        if frame.type != self.frame_type:
            raise ValueError(f"Frame type mismatch: expected {self.frame_type}, got {frame.type}")
        
        if frame.is_valid():
            self.frames.append(frame)
        else:
            raise ValueError(f"Invalid calibration frame: {frame}")

    def get_matching_frames(self, 
                          exposure_time: Optional[float] = None,
                          temperature: Optional[float] = None,
                          gain: Optional[int] = None) -> list[CalibrationFrame]:
        """Возвращает кадры, соответствующие заданным параметрам"""
        matching_frames = self.frames

        if exposure_time is not None:
            matching_frames = [f for f in matching_frames 
                             if f.exposure_time == exposure_time]
            
        if temperature is not None:
            matching_frames = [f for f in matching_frames 
                             if f.temperature == temperature]
            
        if gain is not None:
            matching_frames = [f for f in matching_frames 
                             if f.gain == gain]
            
        return matching_frames

    def clear(self) -> None:
        """Очищает набор кадров"""
        self.frames.clear()
        self._master_frame = None


class CalibrationFrameLibrary:
    def __init__(self):
        self.bias_frames = CalibrationFrameSet(CalibrationFrameType.BIAS)
        self.dark_frames = CalibrationFrameSet(CalibrationFrameType.DARK)
        self.flat_frames = CalibrationFrameSet(CalibrationFrameType.FLAT)

    def get_frame_set(self, frame_type: CalibrationFrameType) -> CalibrationFrameSet:
        """Возвращает набор кадров определенного типа"""
        if frame_type == CalibrationFrameType.BIAS:
            return self.bias_frames
        elif frame_type == CalibrationFrameType.DARK:
            return self.dark_frames
        elif frame_type == CalibrationFrameType.FLAT:
            return self.flat_frames
        else:
            raise ValueError(f"Unknown frame type: {frame_type}")

    def has_calibration_frames(self, frame_type: CalibrationFrameType) -> bool:
        """Проверяет наличие калибровочных кадров определенного типа"""
        frame_set = self.get_frame_set(frame_type)
        return len(frame_set.frames) > 0

    def has_master_frame(self, frame_type: CalibrationFrameType) -> bool:
        """Проверяет наличие мастер-кадра определенного типа"""
        frame_set = self.get_frame_set(frame_type)
        return frame_set.master_frame is not None
