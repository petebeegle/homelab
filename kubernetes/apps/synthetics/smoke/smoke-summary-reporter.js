const MAX_FAILED_TESTS_LENGTH = 512;

function sanitizeLogfmtValue(value) {
  return String(value)
    .replace(/[\r\n\t]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function truncate(value, maxLength = MAX_FAILED_TESTS_LENGTH) {
  if (value.length <= maxLength) {
    return value;
  }
  if (maxLength <= 3) {
    return value.slice(0, maxLength);
  }
  return value.slice(0, maxLength - 3) + "...";
}

function quoteLogfmt(value) {
  return '"' + sanitizeLogfmtValue(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
}

function testTitle(test) {
  if (typeof test.titlePath === "function") {
    const parts = test.titlePath().filter(Boolean);
    return parts[parts.length - 1] || test.title || "unknown test";
  }
  return test.title || "unknown test";
}

function finalFailedTests(suite) {
  if (!suite || typeof suite.allTests !== "function") {
    return [];
  }
  return suite
    .allTests()
    .filter((test) => typeof test.outcome === "function" && test.outcome() === "unexpected")
    .map(testTitle);
}

function formatSummary({ status, failedTests, durationSeconds }) {
  const failedTestText = truncate(failedTests.map(sanitizeLogfmtValue).join("; "));
  return [
    "SMOKE_RUN_SUMMARY",
    "status=" + status,
    "failed_count=" + failedTests.length,
    "failed_tests=" + quoteLogfmt(failedTestText),
    "duration_seconds=" + Math.max(0, Math.round(durationSeconds))
  ].join(" ");
}

class SmokeSummaryReporter {
  constructor(options = {}) {
    this._now = options.now || (() => Date.now());
    this._startMs = undefined;
    this._suite = undefined;
  }

  onBegin(_config, suite) {
    this._startMs = this._now();
    this._suite = suite;
  }

  onEnd(result) {
    const failedTests = finalFailedTests(this._suite);
    const startMs = this._startMs ?? this._now();
    const durationSeconds = (this._now() - startMs) / 1000;
    const status = result.status === "passed" ? "success" : "failed";
    console.log(formatSummary({ status, failedTests, durationSeconds }));
  }
}

module.exports = SmokeSummaryReporter;
module.exports.MAX_FAILED_TESTS_LENGTH = MAX_FAILED_TESTS_LENGTH;
module.exports.finalFailedTests = finalFailedTests;
module.exports.formatSummary = formatSummary;
module.exports.quoteLogfmt = quoteLogfmt;
