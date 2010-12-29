"""Tests to ensure that the lxml tree builder generates good trees."""

from helpers import BuilderInvalidMarkupSmokeTest, BuilderSmokeTest

class TestLXMLBuilder(BuilderSmokeTest):
    """See `BuilderSmokeTest`."""

    def test_bare_string(self):
        # lxml puts a <p> tag around the bare string.
        self.assertSoupEquals(
            "A bare string", "<p>A bare string</p>")


class TestLXMLBuilderInvalidMarkup(BuilderInvalidMarkupSmokeTest):
    """See `BuilderInvalidMarkupSmokeTest`."""

