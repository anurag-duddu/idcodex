import { test, expect } from "@playwright/test";

test("unauthenticated visit to a protected page redirects to sign-in", async ({
  page,
}) => {
  await page.goto("/studio");
  await expect(page).toHaveURL(/\/signin/);
});

test("unauthenticated file API returns 401", async ({ request }) => {
  const res = await request.get(
    "/api/file/00000000-0000-0000-0000-000000000000",
  );
  expect(res.status()).toBe(401);
});
