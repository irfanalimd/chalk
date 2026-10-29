# chalk

chalk is a Claude Code plugin that turns a paper, blog post or announcement into a narrated explainer
video in the style of 3Blue1Brown. You give it a link. It writes the script, animates it with Manim,
records the narration with an ElevenLabs voice, adds music and captions, and renders a 1080p video.
It can also make a simple web page to host the video.

It works on macOS and Linux.

## Install

In Claude Code:

```
/plugin marketplace add irfanalimd/chalk
/plugin install chalk@chalk
```

You also need ffmpeg, a few system libraries and an ElevenLabs API key. [docs/install.md](docs/install.md)
walks through both platforms.

## Make a video

Ask Claude for one, in your own words:

```
Make a chalk video about this paper: <link>. Two minutes, for people with a STEM degree
but no background in the field.
```

```
Make a long chalk video explaining the whole "Attention Is All You Need" paper.
Use the paper's figures where they help.
```

Claude reads the sources, asks a few questions, and shows you the script before it renders anything.

There are two lengths:

- **Short** (the default) is 2–3 minutes on why a result matters.
- **Long** is 8–10 minutes and goes through a whole paper chapter by chapter. Say "long" or "deep dive",
  or ask for a length in that range.

## Revisions

Give notes the way you would to an editor:

```
Make the photo credit smaller and put it under the picture.
Add half a second of pause between topics.
The audio cuts off before the title card. Fix that.
Use a male voice. Save this as v2 and keep v1.
```

Each delivered version is kept, so you can always go back.

## Examples

The `examples/` folder has the full source (script, narration settings and every scene) for two videos:

- `needle-problem/` is a short video on a 2026 result about the Kakeya needle problem.
- `attention-paper/` is a long walkthrough of "Attention Is All You Need".

## More

- [Installation](docs/install.md) for macOS and Linux
- [How it works](docs/how-it-works.md): the pipeline, running steps by hand, project layout and limits
- [A reusable brief](docs/brief.md) you can paste into a project's `CLAUDE.md`
