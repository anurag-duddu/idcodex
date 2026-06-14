import { NextResponse, type NextRequest } from "next/server";
import { getCurrentUser } from "@/auth/session-cookie";
import { isAllowed } from "@/auth/allowlist";
import { getFileNode } from "@/db/queries/nodes";
import { isRemoteUrl, signedUrlFor } from "@/lib/r2";

/**
 * Gated file access. Auth + allowlist, then:
 *  - dev sample (absolute URL key): proxy the bytes inline (no CORS, no leak)
 *  - real key: 302 to a short-lived signed R2 URL (keeps R2's free egress)
 */
export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ nodeId: string }> },
) {
  const user = await getCurrentUser();
  if (!user) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  if (!(await isAllowed(user.email))) {
    return NextResponse.json({ error: "forbidden" }, { status: 403 });
  }

  const { nodeId } = await ctx.params;
  const node = await getFileNode(nodeId);
  if (!node || !node.storageKey) {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }

  if (isRemoteUrl(node.storageKey)) {
    const upstream = await fetch(node.storageKey);
    if (!upstream.ok || !upstream.body) {
      return NextResponse.json({ error: "upstream error" }, { status: 502 });
    }
    return new NextResponse(upstream.body, {
      status: 200,
      headers: {
        "Content-Type":
          node.mimeType ??
          upstream.headers.get("content-type") ??
          "application/octet-stream",
        "Content-Disposition": "inline",
        "Cache-Control": "private, max-age=300",
      },
    });
  }

  const url = await signedUrlFor(node.storageKey, { expiresIn: 300 });
  return NextResponse.redirect(url, 302);
}
