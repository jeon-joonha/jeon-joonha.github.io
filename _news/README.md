# Authoring News Items

To add a new announcement or news item to your website via GitHub:

1. Create a new `.md` file inside the `_news/` directory using the naming convention:
   `YYYY-MM-DD-short-title.md` (e.g. `2026-06-01-conference-presentation.md`).

2. Include the YAML front-matter header at the top of the file:

```yaml
---
layout: post
date: 2026-06-01 09:00:00 +0200
title: "Your Announcement or News Title"
inline: false
---
```

3. **Front-matter options**:
   - `inline: true`: Displays the text inline on the homepage without creating a standalone post page.
   - `inline: false`: Creates a dedicated full news post page.
   - `redirect: "https://..."`: Redirects users clicking the headline directly to an external URL or blog post.

4. Commit the file directly via the GitHub web editor or git, and GitHub Actions will automatically publish the update!
