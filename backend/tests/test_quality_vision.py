# -*- coding: utf-8 -*-
"""
TDD: GeminiVisionAnalyzer behavior tests.
Tests verify public behavior through the analyzer interface only.
"""
import json
import pytest
from app.integrations.gemini_vision_quality import GeminiVisionAnalyzer


# ── Mock helpers ─────────────────────────────────────────────────────────────

class _MockResponse:
    def __init__(self, text):
        self.text = text


class _MockModels:
    def __init__(self, response_text):
        self._text = response_text

    def generate_content(self, *, model, contents, **kwargs):
        return _MockResponse(self._text)


class _MockClient:
    def __init__(self, response_text):
        self.models = _MockModels(response_text)


def _make_analyzer(response_dict: dict) -> GeminiVisionAnalyzer:
    return GeminiVisionAnalyzer(client=_MockClient(json.dumps(response_dict)))


TOMATO_RESPONSE = {
    "detected_crop": "cà chua",
    "is_produce": True,
    "color_assessment": "Màu đỏ tươi đồng đều, không có đốm bất thường",
    "ripeness": "chín đều",
    "defects": [],
    "quality_grade": "grade_1",
    "confidence": 0.92,
    "reasoning": "Cà chua màu đỏ đều, không khuyết tật",
}

NON_PRODUCE_RESPONSE = {
    "detected_crop": "không phải nông sản",
    "is_produce": False,
    "color_assessment": "Ảnh chứa người và đồ vật",
    "ripeness": "unknown",
    "defects": [],
    "quality_grade": "grade_3",
    "confidence": 0.95,
    "reasoning": "Không phát hiện nông sản trong ảnh",
}

GRADE3_RESPONSE = {
    "detected_crop": "xoài",
    "is_produce": True,
    "color_assessment": "Màu nâu đen, nhiều vết bầm",
    "ripeness": "quá chín",
    "defects": ["bầm dập", "biến màu", "nấm mốc"],
    "quality_grade": "grade_3",
    "confidence": 0.85,
    "reasoning": "Xoài bị bầm và biến màu nặng",
}


# ── Test 1 (tracer): analyzer trả về detected_crop và quality_grade ──────────

def test_analyzer_returns_detected_crop_and_grade():
    analyzer = _make_analyzer(TOMATO_RESPONSE)
    result = analyzer.analyze(b"fake_image_bytes")

    assert result["detected_crop"] == "cà chua"
    assert result["quality_grade"] == "grade_1"
    assert result["is_produce"] is True
    assert result["confidence"] == 0.92


# ── Test 2: ảnh không phải nông sản → is_produce=False ───────────────────────

def test_analyzer_detects_non_produce():
    analyzer = _make_analyzer(NON_PRODUCE_RESPONSE)
    result = analyzer.analyze(b"fake_image_bytes")

    assert result["is_produce"] is False
    assert result["detected_crop"] == "không phải nông sản"


# ── Test 3: Gemini trả JSON không hợp lệ → fallback confidence=0.0 ───────────

def test_analyzer_fallback_on_bad_json():
    analyzer = GeminiVisionAnalyzer(client=_MockClient("Đây không phải JSON"))
    result = analyzer.analyze(b"fake_image_bytes")

    assert result["confidence"] == 0.0
    assert result["is_produce"] is False


# ── Test 4: color_assessment có trong kết quả ────────────────────────────────

def test_analyzer_includes_color_assessment():
    analyzer = _make_analyzer(TOMATO_RESPONSE)
    result = analyzer.analyze(b"fake_image_bytes")

    assert "color_assessment" in result
    assert len(result["color_assessment"]) > 0


# ── Test 5: defects được trả về đúng ─────────────────────────────────────────

def test_analyzer_returns_defects_list():
    analyzer = _make_analyzer(GRADE3_RESPONSE)
    result = analyzer.analyze(b"fake_image_bytes")

    assert "defects" in result
    assert isinstance(result["defects"], list)
    assert "bầm dập" in result["defects"]


# ── Test 6: Gemini markdown code fence bị strip đúng cách ────────────────────

def test_analyzer_strips_markdown_fences():
    fenced = "```json\n" + json.dumps(TOMATO_RESPONSE) + "\n```"
    analyzer = GeminiVisionAnalyzer(client=_MockClient(fenced))
    result = analyzer.analyze(b"fake_image_bytes")

    assert result["detected_crop"] == "cà chua"
    assert result["quality_grade"] == "grade_1"
