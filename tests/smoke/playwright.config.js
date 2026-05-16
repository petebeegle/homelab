const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: ".",
  timeout: 30_000,
  expect: {
    timeout: 10_000
  },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["json", { outputFile: "test-results.json" }]] : "list",
  use: {
    baseURL: "https://whoami." + (process.env.SMOKE_BASE_DOMAIN || "lab.petebeegle.com"),
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
    launchOptions: {
      chromiumSandbox: false
    },
    actionTimeout: 10_000,
    navigationTimeout: 20_000
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"]
      }
    }
  ]
});
