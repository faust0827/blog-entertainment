import unittest

from automation import gates


class BasicGatesTests(unittest.TestCase):
    def test_run_gates_returns_results(self):
        html = "<html><body><p>테스트 본문입니다. 장애인 복지에 대한 해설과 분석을 담았습니다.</p><h2>소제목</h2></body></html>"
        results = gates.run_gates(html)
        self.assertTrue(isinstance(results, list))
        self.assertTrue(len(results) > 0)

    def test_failed_filters(self):
        results = gates.run_gates("<p>짧음</p>")
        failures = gates.failed(results)
        self.assertTrue(all(not r.passed for r in failures))

    def test_format_results(self):
        results = gates.run_gates("<p>짧음</p>")
        out = gates.format_results(results, "x.html")
        self.assertIn("게이트", out)


if __name__ == "__main__":
    unittest.main()
