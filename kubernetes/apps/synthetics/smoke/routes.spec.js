const { expect, test } = require("@playwright/test");

const baseDomain = process.env.SMOKE_BASE_DOMAIN || "lab.petebeegle.com";

function urlFor(host, path = "/") {
  return "https://" + host + "." + baseDomain + path;
}

async function gotoOk(page, url) {
  const response = await page.goto(url, { waitUntil: "domcontentloaded" });
  expect(response, url + " should return an HTTP response").not.toBeNull();
  expect(response.status(), url + " should not return a server error").toBeLessThan(500);
  return response;
}

test.describe("homelab routed services", () => {
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
