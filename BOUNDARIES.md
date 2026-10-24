# Where sound and moving pictures live

Two suites touch audio and video, and the question "which package should do
this?" has come up often enough to be worth writing down once.

## The principle

**ai-helpers owns the primitive. sprezzature owns the opinion.**

ai-helpers packages answer "how do I do X to this file" — decode, resample,
separate, transcribe, synthesize, extract frames, mux, compress. They are
general, they take a path and give a path, and they carry no view about what
you should make.

sprezzature packages answer "what should this *be*" — the three-Roboto rule,
twenty a11y rules, a hand-authored SVG rather than an export, a film whose
claims are checked against the code. They are opinionated by design, and they
reach down through the ai-helpers primitives rather than reimplementing them.

The test for a new capability: *would this be the same for someone with
entirely different taste?* If yes it belongs in ai-helpers. If it encodes a
judgement about what good looks like, it belongs in sprezzature.

## The voice, which is four layers deep

| Layer | Owns | Serves |
|---|---|---|
| `speaker-engines` | Model weights, self-hosted. Nothing is fetched from Hugging Face at runtime. | speaker-helper |
| `speaker-helper` | **The engines**: Kokoro, OpenVoice, Chatterbox, Voicebox. espeak-ng handling, voice cloning, the evaluation gate. | sprezzature-audio |
| `sprezzature-audio` | "The sound modality in both directions" — its own words. Drives speaker-helper through `scripts/_speaker.py`; adds captions, diarization, translation, and the suite's one WebVTT module. | publish, video |
| `sprezzature-publish`, `sprezzature-video` | Applying it: a narrated blog post, a film's narration track. | the site |

These are layers, not alternatives. `sprezzature-audio` declares
`narrate = ["speaker-helper[kokoro,detect]>=0.8.0"]`, so Kokoro arrives through
speaker-helper whichever door you knock on. **A sprezzature package wanting a
voice depends on `sprezzature-audio[narrate]`, never on speaker-helper
directly** — the espeak-ng loader can kill a process from C with no Python
traceback, and the handling for that lives one layer down, where it was learned.

`vocal-helper` and `audio-helper` do no synthesis at all. They decode, separate
and diarize. Do not look for a voice there.

## The moving picture

| Layer | Owns |
|---|---|
| `video-helper` | ffmpeg primitives: frame extraction, convert, compress, concat, overlay, `mux_audio_video`, `burn_subtitles`, optical flow. |
| `capture-helper` | Frames out of the room rather than out of a file. |
| `youtube-helper`, `podcast-helper` | Acquisition: a URL in, media out. |
| `sprezzature-figures`, `-maps` | What appears *in* the frame: hand-authored SVG. |
| `sprezzature-video` | What the film **is**: the storyboard, the claims and their verification, the asset ledger, the captions, the poster, the series. |
| Hyperframes (third party, Apache 2.0) | Turning a composition into frames. Held behind a seam; Playwright and a direct ffmpeg path are not excluded. |

Rendering is the one piece this suite does not own and does not want to. It is
the most commoditised step and the least opinionated: the judgement is in the
storyboard and in whether the claims are true, not in the frame grabber.

## Three duplications this audit found

**1. Three paths to Kokoro.** `npx hyperframes tts` (third party, bundled), the
`speaker-helper` engines, and `sprezzature-audio[narrate]` as the suite's door
onto them. The suite's own films were narrated by the **first** — the one
outside both suites. That is how it happened, not how it should stay: the films
should move to `sprezzature-audio[narrate]`. The migration is not free, and the
reason is worth recording — switching engines for part of a series changes the
timbre, so a move means **regenerating all of a film's lines, not some**. Two
lines were regenerated on 2026-10-24 with `hyperframes tts` for exactly that
reason.

**2. Two WebVTT writers.** `sprezzature_audio_scripts._vtt` consolidated four
writers and two readers inside sprezzature and pinned every behavioural
difference in `test_one_vtt.py`. `speaker_helper.cues_to_vtt` is a second one,
in the backend. Both are defensible where they sit — speaker-helper should not
depend on a sprezzature package — but a caption written by one and read by the
other is an untested path. Worth a decision, not an accident.

**3. Duration is split on purpose, and the split leaks.**
`audio_helper.get_audio_duration` and `video_helper.video_duration` are
deliberate mirrors; `video_duration`'s own docstring says so. But handed an
audio-only file it raises a bare `StopIteration` from an internal generator,
which reads as a bug in video-helper rather than as "wrong half of the split".
A clear error naming the other function is the fix — the boundary is right, the
signpost is missing.

## Improvements this suggests for the backend

- `video-helper`: raise a clear, named error on audio-only input instead of
  leaking `StopIteration`, pointing the caller at `audio_helper`.
- `video-helper`: no loudness primitive exists. `sprezzature-video`'s
  `post.normalize_loudness` is the only direct ffmpeg call in this package for
  that reason, and should become a call into video-helper if one lands.
- `speaker-helper` / `sprezzature-audio`: decide which WebVTT writer is
  canonical, or pin the round trip between them with a test.
