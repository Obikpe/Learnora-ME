# Learnora ME — private R2 video delivery and rendering setup

**Status:** implementation source is in the repository; external credentials and the live R2 bucket are not configured by this change. Do not publish courses until the generated videos have been reviewed.

## Storage and access model

- Store all newly produced Course Studio MP4 files—both AI-rendered and human-produced—in a **private Cloudflare R2 bucket**. The current legacy video signer defaults to the private Supabase `learnora-course-media` bucket, and lesson resources use private `learnora-resources`. Pheonix also contains an empty private `learnora-videos` bucket; no lesson-video rows or objects currently depend on it. Do not migrate or delete any of these legacy buckets as part of the Course Studio rollout.
- Store the durable provider and object key in Supabase `lesson_videos` rows (`provider='cloudflare'`, `storage_path`). The bucket name is supplied to the backend through `R2_BUCKET_NAME`; the current `lesson_videos` schema does not have a `storage_bucket` column. Keep the video transcript in `transcript_text`.
- Never store a time-limited signed URL in Supabase.
- The Learnora ME backend verifies the learner's existing course access, then generates a one-hour R2 GET presigned URL. The browser receives only that temporary URL. For human-produced lessons, an authorised staff member requests a short-lived R2 PUT URL from Course Studio; the backend verifies the uploaded object before creating the lesson-video metadata row.
- Internal Course Studio reviewers can also preview ready videos through a separate staff-permission-gated endpoint before publication. Both AI and human video sources use the same private R2 playback path.
- The learner video player uses the returned URL with cross-origin media playback enabled.
- The object key is unique per approved lesson-production package:
  AI render key: `courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/{production_package_id}.mp4`\nHuman upload key: `courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/{upload_uuid}.mp4`

The bucket must remain private. Do not enable public bucket access or put the R2 access keys in frontend environment variables.

## R2 bucket CORS

Create a standard R2 bucket, keep public access disabled, and configure CORS for the production Learnora ME origin and local development. Add the actual custom production domain too if the site later moves away from `learnorame.vercel.app`.

```json
[
  {
    "AllowedOrigins": [
      "https://learnorame.vercel.app",
      "https://learnora-me.vercel.app",
      "http://localhost:3000"
    ],
    "AllowedMethods": ["GET", "HEAD", "PUT"],
    "AllowedHeaders": ["Range", "Content-Type"],
    "ExposeHeaders": [
      "Accept-Ranges",
      "Content-Length",
      "Content-Range",
      "ETag"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

The backend signs GET access for playback and short-lived PUT access for authorised Course Studio uploads. Uploads happen only in the internal staff workflow, never on learner pages. The Team content workspace also uploads human-produced videos for AI-generated courses through this same R2 path, so its production origin (`learnora-me.vercel.app`) must be allowed by the bucket CORS policy.

## Required environment variables

### Vercel — Learnora ME backend

Add these to the backend project (`learnora-backend`) for the production environment and any preview environment that needs to play private videos:

- `R2_ACCOUNT_ID`
- `R2_BUCKET_NAME`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

The backend needs R2 object read/write permission: it signs GET URLs for playback, signs PUT URLs for human-produced video uploads, and verifies uploaded objects. Use a bucket-scoped R2 API token; never expose it to browser code.

### GitHub — repository Actions secrets

In `Obikpe/Learnora-ME` → Settings → Secrets and variables → Actions, add:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `R2_ACCOUNT_ID`
- `R2_BUCKET_NAME`
- `R2_WORKER_ACCESS_KEY_ID` (worker read/write token)
- `R2_WORKER_SECRET_ACCESS_KEY` (worker read/write token)

The worker reads `R2_WORKER_ACCESS_KEY_ID` and `R2_WORKER_SECRET_ACCESS_KEY` for its separate R2 read/write token. The backend reads `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` from its Vercel environment for signed playback, human uploads and object verification. The worker needs Supabase service-role access to claim render jobs and update lesson media metadata. Keep the backend token separate from the worker token. These secrets must never be committed to the repository, printed in logs, or exposed to browser code.

## Rendering worker

Course Studio records the selected source per lesson. AI-source lessons are rendered by the worker; human-source lessons skip the AI render queue and are uploaded directly to the same private R2 bucket using the staff-only signed PUT flow. Existing older human-uploaded media remains in Supabase Storage.

The repository now contains:

- `scripts/video_renderer/worker.py`
- `scripts/video_renderer/requirements.txt`
- `.github/workflows/learnora-video-renderer.yml`

The workflow checks the required secrets and skips safely if they are absent. Once configured, it checks the queue every five minutes and can also be started manually from GitHub Actions.

The worker:

1. Claims a queued job through a service-role-only Supabase RPC.
2. Loads the approved private teaching script and visual storyboard.
3. Generates English narration with the quantized Kokoro ONNX model.
4. Renders deterministic 720p slide, diagram, table, code and guided-step scenes with captions.
5. Encodes a browser-friendly H.264/AAC MP4 with FFmpeg.
6. Uploads the file to the private R2 bucket.
7. Creates or updates the private `lesson_videos` record and marks the render job complete.

This is a **narrated visual lesson renderer**, not a cinematic text-to-video service. It avoids sending equations, code or instructional text to an image/video model that could distort them. Software-specific real screen recordings and richer Excel/browser demonstrations can be added as dedicated renderers.

The render queue includes retries and stale-job recovery. A course remains a draft while videos are being rendered; successful rendering does not publish it.

## Cost and licensing notes

The Learnora ME repository is public. GitHub documents that standard hosted runners are free for public repositories; this makes Actions a practical pilot worker without a separate rendering-server bill. If repository visibility changes, re-check GitHub Actions billing before relying on this assumption.

The Kokoro ONNX Python package is MIT-licensed and the Kokoro 82M model is Apache-2.0. The model is downloaded by the worker and its SHA-256 checksum is verified before use. R2 storage and request allowances still have limits; monitor usage rather than assuming unlimited free storage.

## Release checklist

- [ ] Create the private R2 bucket.
- [ ] Create a bucket-scoped R2 API token with object read/write access.
- [ ] Configure the R2 CORS policy above, adding any real custom domain.
- [ ] Add the four R2 variables to the Vercel backend environment with bucket-scoped read/write permission.
- [ ] Add the six GitHub worker secrets (Supabase URL/key, R2 account/bucket and the separate worker access/secret key) to GitHub Actions.
- [ ] Apply the pending Course Studio/video-render migration to live Pheonix only after the migration rehearsal passes and the release is approved.
- [ ] Deploy the backend and Learnora ME frontend only after the migration is applied.
- [ ] Run one AI-video lesson and one human-video lesson end to end; verify the R2 MP4/captions, private R2 human upload, staff previews, signed learner playback URLs and learner access restrictions.
- [ ] Review the video and lesson content before publishing the course.


## Primary references

- [Cloudflare R2 presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/)
- [Cloudflare R2 bucket CORS](https://developers.cloudflare.com/r2/buckets/cors/)
- [GitHub Actions billing and public-repository runner usage](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Kokoro ONNX implementation and usage](https://github.com/thewh1teagle/kokoro-onnx)
- [Kokoro 82M ONNX model and licence](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX)
