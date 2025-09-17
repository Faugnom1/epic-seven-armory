Epic Seven Armory

A simple desktop companion for Epic Seven to store your units, upload screenshots, and auto-read stats with OCR. Sign in with Google, look up every E7 unit, and (optionally) connect a Twitch Extension so viewers can see your roster.

[IMAGE: docs/images/banner.png]

WHAT YOU CAN DO

• Unit storage — keep a personal roster of your heroes with portraits and stats.
• Upload & auto-read — drag a screenshot in; the app reads text and numbers with OCR (you can edit anything).
• Full unit lookup — search the entire Epic Seven catalog by name, element, class, rarity, etc.
• Google sign-in — log in with your Google account to keep your profile consistent.
• Twitch extension (optional) — let chat browse your roster while you stream.
• Screenshots & archives — save raw screenshots and cropped portraits for sharing.
• Coming soon — link to the SIFT Draft Matcher to auto-detect your 4 picks and the banned unit on the post-ban screen.

[IMAGE: docs/images/roster-grid.png]

WHO THIS IS FOR

Players who want an easy way to keep their roster tidy, upload a screenshot and let the app read the text, look up units and plan builds, and optionally share the roster on stream. No command line required for normal use.

GETTING STARTED (QUICK)

Download and open the latest Windows build.

Optional but recommended: click “Sign in with Google.” Your Google password is never shared with the app.

Add your units: upload screenshots (single or batch). The app will read text automatically; review and edit as needed.

Search and share: use Unit Lookup to filter by name/element/class; export images or links to share.

[IMAGE: docs/images/upload-flow.png]

KEY FEATURES IN DETAIL

Unit storage
• Personal roster with portraits, levels, and key stats
• Bulk add from a folder
• Quick edit any field the OCR didn’t get perfectly

Upload & decipher (OCR)
• Uses PyTesseract to read in-game text from screenshots
• Works best with 1920×1080 screenshots, UI scale 100%, and clear fonts
• Re-run OCR on a crop or correct values manually

Full unit lookup
• Browse every Epic Seven unit
• Filter by name, element, class, rarity, and role
• Jump from lookup → add to roster → edit stats

Sign in with Google
• One-click sign-in using Google OAuth
• The app receives a short-lived token; it never sees your password
• You can use the app locally without signing in if you prefer

Twitch extension (optional)
• Connect your Twitch account and enable the companion extension
• Viewers can browse your roster while you stream
• You control what’s visible

[IMAGE: docs/images/twitch-extension.png]

FAQ (SHORT)

Does OCR always get everything right?
• Not always; fonts and effects can confuse OCR. Click any field to edit quickly.

What screenshots work best?
• Full-resolution (e.g., 1920×1080), UI scale 100%, uncompressed PNG if possible.

Do I have to log in with Google?
• No. You can use the app locally without sign-in. Google login just keeps your profile consistent across sessions.

Where do my images go?
• Locally in your screenshots and hero_images folders. You control what you share.

Is my Google data safe?
• Sign-in uses Google’s standard OAuth page. The app gets a token to identify you; it never sees your password.

ROADMAP / COMING SOON

• SIFT Draft Matcher integration (auto-detect 4 picks + banned unit on the post-ban screen)
• Better OCR tuned for specific screens
• Team builder and comparisons
• Export packs for sharing to Discord/Twitter
• Optional cloud sync

[IMAGE: docs/images/coming-soon.png]

TROUBLESHOOTING (QUICK)

• OCR is wrong or blank → try a clearer screenshot, avoid motion blur, set UI scale to 100%, or crop tighter around the text and retry.
• Can’t sign in → make sure your system clock is correct and pop-ups to Google’s sign-in page aren’t blocked.
• Twitch extension not showing → re-link your Twitch account and ensure the extension is enabled on your channel’s dashboard.

If you’re stuck, open an issue with a screenshot and a short description of what happened.

FEEDBACK

• Found a bug or have an idea? Open an Issue on GitHub.
• Pull Requests are welcome—small, focused changes work best.

DEVELOPER NOTES (OPTIONAL)

• Windows is the primary target.
• Secrets like google_oauth.json and .env are ignored by Git—keep them local.
• If you prefer running from source, see the developer docs in the repo for dependency lists and scripts.

Enjoy, and happy hunting! 🛡️
