import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";
import { type Page } from "@playwright/test";

/**
 * Sign in through Clerk in an e2e run.
 *
 * Requires Clerk testing mode: set CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY in
 * the Playwright env and a test user (e.g. an `id.iit.edu` address) whose
 * password is in E2E_CLERK_USER_PASSWORD. See
 * https://clerk.com/docs/testing/playwright/overview
 */
export async function signIn(
  page: Page,
  identifier = process.env.E2E_CLERK_USER ?? "tester@id.iit.edu",
) {
  await setupClerkTestingToken({ page });
  await page.goto("/sign-in");
  await clerk.signIn({
    page,
    signInParams: {
      strategy: "password",
      identifier,
      password: process.env.E2E_CLERK_USER_PASSWORD ?? "",
    },
  });
  await page.goto("/");
}
