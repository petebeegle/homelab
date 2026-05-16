const assert = require("node:assert/strict");
const test = require("node:test");

const SmokeSummaryReporter = require("./smoke-summary-reporter");
const { MAX_FAILED_TESTS_LENGTH, MAX_RUN_NAME_LENGTH, finalFailedTests } = SmokeSummaryReporter;

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

async function withEnv(updates, fn) {
  const original = new Map(Object.keys(updates).map((key) => [key, process.env[key]]));

  for (const [key, value] of Object.entries(updates)) {
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }

  try {
    return await fn();
  } finally {
    for (const [key, value] of original.entries()) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
}

test("reporter emits a successful bounded summary", async () => {
  const timestamps = [1_000, 38_000];
  const reporter = new SmokeSummaryReporter({ now: () => timestamps.shift() });
  const line = await withEnv({ SMOKE_RUN_NAME: "synthetic-smoke-28925520", HOSTNAME: "pod-hostname" }, () =>
    captureReporterLine(reporter, { status: "passed" }, makeSuite([]))
  );

  assert.equal(line, 'SMOKE_RUN_SUMMARY run="synthetic-smoke-28925520" status=success failed_count=0 failed_tests="" duration_seconds=37');
});

test("reporter records only final failed tests after retries with escaping and truncation", async () => {
  const longTitle = 'pihole root redirects to the "admin" shell with slash \\ ' + "x".repeat(600);
  const longRunName = 'synthetic "manual" run \\ ' + "x".repeat(200);
  const suite = makeSuite([
    makeTest("whoami exercises Gateway TLS and routing", "flaky"),
    makeTest(longTitle, "unexpected")
  ]);
  const failedTests = finalFailedTests(suite);
  const timestamps = [2_000, 44_000];
  const reporter = new SmokeSummaryReporter({ now: () => timestamps.shift() });
  const line = await withEnv({ SMOKE_RUN_NAME: undefined, HOSTNAME: longRunName }, () =>
    captureReporterLine(reporter, { status: "failed" }, suite)
  );
  const runField = line.match(/run="((?:\\"|\\\\|[^"])*)"/)[1];
  const failedTestsField = line.match(/failed_tests="((?:\\"|\\\\|[^"])*)"/)[1];

  assert.deepEqual(failedTests, [longTitle]);
  assert.match(line, /^SMOKE_RUN_SUMMARY run="synthetic \\"manual\\" run \\\\ /);
  assert.match(line, / status=failed failed_count=1 failed_tests="/);
  assert.ok(runField.length <= MAX_RUN_NAME_LENGTH + 4);
  assert.equal(runField.endsWith("..."), true);
  assert.match(line, /\\"admin\\"/);
  assert.match(line, /slash \\\\/);
  assert.doesNotMatch(line, /\n|\r/);
  assert.ok(failedTestsField.length <= MAX_FAILED_TESTS_LENGTH + 4);
  assert.equal(failedTestsField.endsWith("..."), true);
  assert.match(line, /duration_seconds=42$/);
});
