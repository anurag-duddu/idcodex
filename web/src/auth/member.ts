import { cache } from "react";
import { getCurrentUserEmail } from "./current-user";
import { isAllowed } from "./allowlist";

/**
 * Whether the signed-in user may see the archive (auto-domain or allowlisted).
 * Cached per request.
 *
 * Every page and generateMetadata in (app) checks this before reading data.
 * The (app) layout's gate is not enough on its own: in the App Router a page
 * renders into the response (RSC payload) alongside its layout, so a layout
 * that shows <NoAccess> instead of its children still ships the page's data.
 */
export const isMember = cache(async (): Promise<boolean> => {
  const email = await getCurrentUserEmail();
  return !!email && (await isAllowed(email));
});
