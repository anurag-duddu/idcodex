import { expect, type Page } from "@playwright/test";

/** Sign in via the dev magic-link (returned inline outside production). */
export async function signIn(page: Page, email = "tester@hawk.iit.edu") {
  await page.goto("/signin");
  await page.fill('input[name="email"]', email);
  await page.getByRole("button", { name: /sign-in link/i }).click();
  const devLink = page.getByRole("link", { name: /Dev link/i });
  await expect(devLink).toBeVisible();
  const href = await devLink.getAttribute("href");
  await page.goto(href!);
  await expect(page).toHaveURL(/localhost:\d+\/?$/);
}
