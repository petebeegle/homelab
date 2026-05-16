const assert = require("node:assert/strict");
const test = require("node:test");

const SmokeSummaryReporter = require("./smoke-summary-reporter");
const { MAX_FAILED_TESTS_LENGTH, finalFailedTests } = SmokeSummaryReporter;

function makeSuite(tests) {
  return {
    allTests() {
      return tests;
    }
  };
}

function makeTest(title, outcome) {
  return {
    title,
    titlePath() {
      return ["", "homelab routed services", title];
    },
    outcome() {
      return outcome;
    }
  };
}

async function captureReporterLine(reporter, result, suite) {
  const lines = [];
  const originalLog = console.log;
  console.log = (line) => lines.push(line);
  try {
    reporter.onBegin({}, suite);
    await reporter.onEnd(result);
  } finally {
    console.log = originalLog;
  }
  assert.equal(lines.length, 1);
  return lines[0];
}

test("reporter emits a successful bounded summary", async () => {
  const timestamps = [1_000, 38_000];
  const reporter = new SmokeSummaryReporter({ now: () => timestamps.shift() });
  const line = await captureReporterLine(reporter, { status: "passed" }, makeSuite([]));

  assert.equal(line, 'SMOKE_RUN_SUMMARY status=success failed_count=0 failed_tests="" duration_seconds=37');
});

test("reporter records only final failed tests after retries with escaping and truncation", async () => {
  const longTitle = 'pihole root redirects to the "admin" shell with slash \\ ' + "x".repeat(600);
  const suite = makeSuite([
    makeTest("whoami exercises Gateway TLS and routing", "flaky"),
    makeTest(longTitle, "unexpected")
  ]);
  const failedTests = finalFailedTests(suite);
  const timestamps = [2_000, 44_000];
  const reporter = new SmokeSummaryReporter({ now: () => timestamps.shift() });
  const line = await captureReporterLine(reporter, { status: "failed" }, suite);
  const failedTestsField = line.match(/failed_tests="((?:\\"|\\\\|[^"])*)"/)[1];

  assert.deepEqual(failedTests, [longTitle]);
  assert.match(line, /^SMOKE_RUN_SUMMARY status=failed failed_count=1 failed_tests="/);
  assert.match(line, /\\"admin\\"/);
  assert.match(line, /slash \\\\/);
  assert.doesNotMatch(line, /\n|\r/);
  assert.ok(failedTestsField.length <= MAX_FAILED_TESTS_LENGTH + 4);
  assert.equal(failedTestsField.endsWith("..."), true);
  assert.match(line, /duration_seconds=42$/);
});
