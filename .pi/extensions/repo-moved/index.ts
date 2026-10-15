/**
 * Tells a pi user that Ailly moved to davidsouther/ailly. One line at session
 * start; general/scripts/migrate-to-ailly.py repoints the install.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const NOTICE =
	"Ailly moved to davidsouther/ailly; this install receives no further updates. " +
	"Run `python3 general/scripts/migrate-to-ailly.py` (dry run first) to repoint it.";

export default function (pi: ExtensionAPI) {
	pi.on("session_start", async (_event, ctx) => {
		if (ctx.hasUI) ctx.ui.notify(NOTICE, "warning");
	});
}
