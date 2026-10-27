# Real footage and stills

Use one or two inserts, a few seconds each, where they add a real person or a real document: the
mathematician who proved the previous case, the paper's abstract with the key sentence highlighted.
Footage is evidence, not decoration.

## Finding it

```bash
yt-dlp --flat-playlist --print "%(id)s | %(channel)s | %(duration_string)s | %(title)s" "ytsearch8:<query>"
yt-dlp --skip-download --print "%(upload_date)s | %(license)s | %(description).600s" <url>
yt-dlp -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]" -o "clips/<name>.%(ext)s" <url>
```

Prefer the institution's own channel (foundations, universities, prize committees). Respect the
user's footage policy (Creative Commons only, or short fair-use clips). Record the URL in
`project.json` `inserts.<name>.source_url` and credit it.

## Choosing shots

1. Contact sheet every 8 s across the source (`sheet.py` with `times=`), then a 1 s sheet around the
   candidates. Note where the source cuts so no shot crosses a cut.
2. Confirm who is on screen from the video's title/description before writing "this is X", and tell
   the user who it is.
3. Make the insert at least as long as its on-screen window; otherwise the last frame freezes.

## Cropping and grading

Many profile videos have burned-in subtitles and a corner logo. Crop per shot, keeping 16:9:
`crop=iw*0.79:ih*0.79:iw*0.105:ih*0.035` keeps the top 79 % and trims the sides. Check a full-res frame
of each shot for leftover subtitle edges. `clips.py` scales to the box, lightly desaturates (0.88) and
adds contrast so footage sits in the dark palette; assembly rounds the corners and fades it in and out.

## Stills

- Archival photos: Wikimedia Commons (check the licence via the `imageinfo`/`extmetadata` API). Tint
  monochrome scans sepia with PIL; credit them in tiny type under the image's bottom-right corner.
- Paper pages: render with PyMuPDF at ~300 dpi; get highlight boxes from `page.search_for(phrase)` and
  map them into image coordinates so highlights sit exactly on the words.
- Use a generic User-Agent for API requests; never the user's email.
