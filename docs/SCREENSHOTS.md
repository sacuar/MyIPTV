# Managing BANG IPTV screenshots on GitHub

The images in [README.md](../README.md) are displayed in the **Screenshot** section. They are currently GitHub-hosted image attachments, **not editable files inside this repository**. To replace or crop them, upload a new image and change the Markdown reference.

## Replace the visible screenshot

1. Take a screenshot of BANG IPTV on Windows. Crop in Paint, Photos or another editor as needed. Consider hiding personal playlists, account details, tokens or URLs.
2. Open the [screenshots folder](../screenshots) in this repository, select **Add file → Upload files**, drop your `.png` or `.webp` image there, then **Commit changes**.
3. Open [README.md](../README.md), choose **Edit** (pencil icon), and find **`## Screenshot`**.
4. Replace only the address inside the screenshot image Markdown. Example:

   ```markdown
   ![BANG IPTV v4 interface](screenshots/bang-iptv-v4.png)
   ```

5. Choose **Preview** and **Commit changes**. The image displayed on the repository's homepage will update.

For two screenshots, add two Markdown image lines pointing at two uploaded files. Using repository-relative paths makes future editing straightforward.

## Distinguish versions

The README currently includes a historical screenshot of the **August 2026 original app**. Do not describe it as v4 unless you upload an actual v4 screenshot.

Suggested filename convention:

- `screenshots/bang-iptv-original.png`
- `screenshots/bang-iptv-v4-player.png`
- `screenshots/bang-iptv-v4-channel-list.png`

A screenshot is an illustration of the interface, not proof that every listed channel is working. Prefer screenshots that show the entire app window without private URLs or other people's account details.

## GitHub mobile browser

If the **Edit** pencil or **Upload files** control is missing on mobile, enable your browser's desktop-site mode or use a PC.
