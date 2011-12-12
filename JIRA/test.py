import unittest, re

from jira import re_make_pattern, re_get_issue

class TestSnarfer(unittest.TestCase):
    def test_regex(self):
        pattern = re_make_pattern(["FOO", "BAR"])
        self.assertEqual(0, len([re_get_issue(m) for m in re.finditer(pattern, "hello world")]))
        self.assertEqual(0, len([re_get_issue(m) for m in re.finditer(pattern, "FOO-1-2")]))
        self.assertEqual(["FOO-123"], [re_get_issue(m) for m in re.finditer(pattern, "FOO-123 world")])
        self.assertEqual(["FOO-123"], [re_get_issue(m) for m in re.finditer(pattern, "hello FOO-123")])
        self.assertEqual(["FOO-123", "BAR-000"], [re_get_issue(m) for m in re.finditer(pattern, "FOO-123 BAR-000")])
        self.assertEqual(["FOO-123", "BAR-000"], [re_get_issue(m) for m in re.finditer(pattern, "hello FOO-123 world BAR-000 hello")])

if __name__ == "__main__":
    unittest.main()
