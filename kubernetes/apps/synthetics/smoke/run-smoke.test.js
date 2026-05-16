const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const path = require("node:path");
const test = require("node:test");

const scriptPath = path.join(__dirname, "run-smoke.sh");

function runWrapper(command) {
  return spawnSync("bash", [scriptPath], {
    cwd: __dirname,
    encoding: "utf8",
    env: {
      ...process.env,
      SMOKE_PLAYWRIGHT_COMMAND: command
    }
  });
}

test("wrapper preserves a successful reporter summary without adding another line", () => {
  const result = runWrapper("printf '%s\\n' 'SMOKE_RUN_SUMMARY status=success failed_count=0 failed_tests=\"\" duration_seconds=37'");
  const summaryLines = result.stdout.split("\n").filter((line) => line.startsWith("SMOKE_RUN_SUMMARY "));

  assert.equal(result.status, 0);
  assert.deepEqual(summaryLines, ['SMOKE_RUN_SUMMARY status=success failed_count=0 failed_tests="" duration_seconds=37']);
});

test("wrapper emits one fallback summary and preserves non-zero exit when Playwright fails before reporter output", () => {
  const result = runWrapper("printf '%s\\n' 'setup exploded'; exit 42");
  const output = result.stdout + result.stderr;
  const summaryLines = output.split("\n").filter((line) => line.startsWith("SMOKE_RUN_SUMMARY "));

  assert.equal(result.status, 42);
  assert.equal(summaryLines.length, 1);
  assert.match(summaryLines[0], /^SMOKE_RUN_SUMMARY status=failed failed_count=0 failed_tests="playwright execution failed before reporter summary" duration_seconds=\d+$/);
});
