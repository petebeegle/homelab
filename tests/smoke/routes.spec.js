const { expect, test } = require("@playwright/test");

const baseDomain = process.env.SMOKE_BASE_DOMAIN || "lab.petebeegle.com";

function urlFor(host, path = "/") {
  const prefix = host ? host + "." : "";
  return "https://" + prefix + baseDomain + path;
}

async function gotoOk(page, url) {
  const response = await page.goto(url, { waitUntil: "domcontentloaded" });
  expect(response, url + " should return an HTTP response").not.toBeNull();
  expect(response.status(), url + " should not return a server error").toBeLessThan(500);
  return response;
}

async function expectNotHomeAssistantOnboarding(page) {
  const pageUrl = new URL(page.url());
  const bodyText = await page.locator("body").innerText({ timeout: 5_000 }).catch(() => "");
  const onboardingDetected =
    /\/onboarding\.html$/i.test(pageUrl.pathname) || /Create my smart home|first[- ]run onboarding|onboarding/i.test(bodyText);

  expect(
    onboardingDetected,
    "Home Assistant is serving first-run onboarding; confirm the GitOps onboarding seed is mounted and verify Authentik OIDC before accepting production smoke."
  ).toBe(false);
}

test.describe("homelab routed services", () => {
  test("homepage serves the dashboard at the root domain", async ({ page }) => {
    await gotoOk(page, urlFor(""));
    await expect(page.locator("body")).toContainText(/Home Lab|Core|Operations|Homepage/i);
  });

  test("whoami exercises Gateway TLS and routing", async ({ page }) => {
    await gotoOk(page, urlFor("whoami"));
    await expect(page.locator("body")).toContainText(/Hostname|IP|RemoteAddr|GET \//i);
  });

  test("authentik serves the unauthenticated start page", async ({ page }) => {
    await gotoOk(page, urlFor("authentik"));
    await expect(page.locator("body")).toContainText(/authentik|Sign in|Login|Username/i);
  });

  test("grafana reaches the login or landing shell", async ({ page }) => {
    await gotoOk(page, urlFor("monitoring"));
    await expect(page.locator("body")).toContainText(/Grafana|Login|Sign in|Welcome/i);
  });

  test("jellyfin reaches the public web shell", async ({ page }) => {
    await gotoOk(page, urlFor("jellyfin"));
    await expect(page.locator("body")).toContainText(/Jellyfin|Please sign in|Wizard|Login/i);
  });

  test("immich reaches OIDC or Authentik login", async ({ page }) => {
    const response = await gotoOk(page, urlFor("immich"));
    test.skip(!process.env.CI && response.status() === 404, "Immich route is not deployed in the live production cluster yet");
    await expect(page).toHaveURL(/authentik\.|immich\.[^/]+\/auth\/login/i);
    await expect(page.locator("body")).toContainText(/Immich|Authentik|Sign in|Login|Username/i);
  });

  test("home assistant reaches OIDC or Authentik login without onboarding", async ({ page }) => {
    const response = await gotoOk(page, urlFor("homeassistant"));
    test.skip(!process.env.CI && response.status() === 404, "Home Assistant route is not deployed in the live production cluster yet");
    await expectNotHomeAssistantOnboarding(page);
    await expect(page).toHaveURL(/authentik\.|homeassistant\.[^/]+\/auth\/oidc\/(?:welcome|redirect|callback)/i);
    await expect(page.locator("body")).toContainText(/Home Assistant|Authentik|Sign in|Login|Username/i);
  });

  test("pihole root redirects to the admin shell", async ({ page }) => {
    await gotoOk(page, urlFor("pihole"));
    await expect(page).toHaveURL(/\/admin(?:\/|\/login)?$/);
    await expect(page.locator("body")).toContainText(/Pi-hole|Sign in|Login|Password/i);
  });

  test("foundry reaches the unauthenticated application shell", async ({ page }) => {
    await gotoOk(page, urlFor("foundry"));
    await expect(page.locator("body")).toContainText(/Foundry|Game Worlds|Administration|Join Game Session|Setup/i);
  });
});
