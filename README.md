# Epic Seven Armory

A desktop companion for Epic Seven to store your units and display them on your twitch steam.

• Unit storage — keep a personal roster of your heroes with portraits and stats.  
• Upload & auto-read — drag a screenshot in; the app reads text and numbers with OCR (you can edit anything).  
• Full unit lookup — search the entire Epic Seven catalog by name for their element, class, rarity, skills, etc.  
• Google sign-in — log in with your Google account to keep your profile consistent.  
• Twitch extension — let viewers browse your pvp team's stats while you stream.  

![alt text](https://github.com/Faugnom1/epic-seven-armory/blob/master/EpicSevenArmory.png)

### GETTING STARTED

Download and open the latest Windows build.

Click “Sign in with Google.” Your Google password is never shared with the app.

Add your units: upload screenshots or through a fribbles json export. The app will read text automatically; review and edit as needed.

Search: use Unit Lookup to filter by name as see their element, class, rarity, skills, etc.

Set up your twitch extension: Add Epic Seven Armory to your twitch extensions and link your account to display your units on stream.

[IMAGE: docs/images/upload-flow.png]

### Draft Detection 

[IMAGE: docs/images/twitch-extension.png]

### FAQ (SHORT)

Does OCR always get everything right?
• Not always; fonts and effects can confuse OCR. Click any field to edit quickly.

What screenshots work best?
• Full-resolution (e.g., 1920×1080), UI scale 100%, uncompressed PNG if possible.

Where do my images go?
• Locally in your screenshots and hero_images folders. You control what you share.

Is my Google data safe?
• Sign-in uses Google’s standard OAuth page. The app gets a token to identify you; it never sees your password.

ROADMAP / COMING SOON

• SIFT Draft Matcher integration (auto-detect 4 picks + banned unit on the post-ban screen)
• Better OCR tuned for specific screens
• Team builder and comparisons
• Export packs for sharing to Discord/Twitter

[IMAGE: docs/images/coming-soon.png]

TROUBLESHOOTING (QUICK)

• OCR is wrong or blank → try a clearer screenshot, avoid motion blur, set UI scale to 100%, or crop tighter around the text and retry.
• Can’t sign in → make sure your system clock is correct and pop-ups to Google’s sign-in page aren’t blocked.
• Twitch extension not showing → re-link your Twitch account and ensure the extension is enabled on your channel’s dashboard.

If you’re stuck, open an issue with a screenshot and a short description of what happened.

FEEDBACK

• Found a bug or have an idea? Open an Issue on GitHub.
• Pull Requests are welcome—small, focused changes work best.
