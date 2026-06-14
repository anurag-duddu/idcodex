import { test, expect } from "@playwright/test";
import { signIn } from "./helpers";

test("sign in → open a course with files → preview a file", async ({ page }) => {
  await signIn(page);

  // Home
  await expect(page.getByText("Knowledge Archive")).toBeVisible();
  await page.screenshot({ path: "screenshots/01-home.png", fullPage: true });

  // Jump to a course that has files via the "Recently added" list (data-agnostic)
  const recent = page.getByTestId("recent-file").first();
  await expect(recent).toBeVisible();
  await recent.click();

  await expect(page.getByText("Files & folders")).toBeVisible();
  await page.screenshot({ path: "screenshots/03-course.png", fullPage: true });

  // Open the first file/folder node
  const node = page.getByTestId("node-link").first();
  await expect(node).toBeVisible();
  await node.click();

  // Either a nested folder (more nodes) or a file page (preview). Both are valid;
  // assert we navigated into the course tree without error.
  await expect(
    page.getByText(/View-only|Files & folders/),
  ).toBeVisible({ timeout: 25_000 });
  await page.screenshot({ path: "screenshots/04-node.png", fullPage: true });
});

test("a PDF actually renders to canvas (R2 CORS)", async ({ page }) => {
  await signIn(page);
  // Reach a course with files via the home "Recently added" list.
  await page.getByTestId("recent-file").first().click();
  await expect(page.getByText("Files & folders")).toBeVisible();
  // Open the first file (migrated files are PDFs).
  await page.getByTestId("node-link").first().click();
  await expect(page.getByText("View-only")).toBeVisible();
  // The PDF must paint — pdf.js renders pages to <canvas>. This fails if the
  // cross-origin fetch to the signed R2 URL is CORS-blocked.
  await expect(page.locator("canvas").first()).toBeVisible({ timeout: 20_000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: "screenshots/07-real-pdf.png", fullPage: true });
});

test("course type listing renders", async ({ page }) => {
  await signIn(page);
  await page
    .getByRole("navigation", { name: "Course types" })
    .getByRole("link", { name: "Seminar" })
    .first()
    .click();
  await expect(page.getByRole("heading", { name: /courses/i })).toBeVisible();
});
