import unittest

from ai.risk_object import TemporalRiskValidator


class TemporalRiskValidatorTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "label": "gun",
            "confidence": 0.35,
            "bbox": [10.0, 10.0, 30.0, 40.0],
        }

    def test_requires_repeated_evidence(self):
        validator = TemporalRiskValidator()
        self.assertEqual(validator.update([self.candidate], 0.0), [])
        confirmed = validator.update(
            [{**self.candidate, "bbox": [12.0, 11.0, 32.0, 41.0]}], 0.1
        )
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0]["temporal_hits"], 2)

    def test_strong_full_frame_candidate_can_alert_immediately(self):
        validator = TemporalRiskValidator()
        confirmed = validator.update(
            [{**self.candidate, "confidence": 0.85, "validation_weight": 1.0}], 0.0
        )
        self.assertEqual(len(confirmed), 1)

    def test_unattended_tile_requires_more_evidence(self):
        validator = TemporalRiskValidator()
        tile = {**self.candidate, "confidence": 0.85, "validation_weight": 0.5}
        for timestamp in (0.0, 0.2, 0.4):
            self.assertEqual(validator.update([tile], timestamp), [])
        self.assertEqual(len(validator.update([tile], 0.6)), 1)

    def test_distant_boxes_do_not_confirm_each_other(self):
        validator = TemporalRiskValidator()
        validator.update([self.candidate], 0.0)
        distant = {**self.candidate, "bbox": [500.0, 500.0, 530.0, 550.0]}
        self.assertEqual(validator.update([distant], 0.1), [])


if __name__ == "__main__":
    unittest.main()
