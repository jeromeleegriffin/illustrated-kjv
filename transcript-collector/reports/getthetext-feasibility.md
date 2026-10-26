# GetTheText / YouTubeText investigation — 2026-10-22

The user's previously successful link is https://www.youtubetext.com/watch?v=Loj1QDHxH3E . The browser observed a redirect to https://getthetext.com/get-transcript?v=Loj1QDHxH3E . Persistent Cloudflare verification blocked this cloud browser. No bypass, account creation, purchase or external contact was attempted.

## What is documented

- Homepage https://getthetext.com/ says it retrieves manual/automatic caption tracks, does not download the video, and caches transcripts for a few days. Exports include TXT, Markdown, JSON, SRT and VTT. Videos lacking captions are unsupported.
- Bulk page https://getthetext.com/bulk-youtube-transcripts accepts pasted video URLs, deduplicates them, produces ZIPs, and reports videos without captions. This is a caption retrieval service, not evidence of an audio-to-text fallback.
- Developer's public portfolio https://www.toptal.com/developers/resume/mikayel-ghukasyan claims a FastAPI backend with caching/rate limiting, server-rendered frontend, VPS/nginx/Cloudflare deployment and GitHub Actions. This is the author's description, not an independent code inspection. Exact upstream caption access, dependencies and implementation remain undisclosed.
- Terms https://getthetext.com/terms instruct users to use its provided bulk tools and prohibit scraping/automating web requests and reverse engineering. We did not implement a scraper or guess internal API endpoints.

## Pricing uncertainty

Pricing https://getthetext.com/pricing advertises free 25/day; Plus $6/month for 300/day; Pro $15/month for 2,000/day and API access (5,000 monthly calls). But terms still say paid plans are not on sale. Public API documentation, actual plan availability, API terms and successful archive coverage are unverified. No purchase recommended as a guaranteed solution.

For 1,294 caption-bearing videos, theoretical free throughput is 52 days at 25/day, Plus five days at 300/day, or Pro one day at 2,000/day. These are quota arithmetic only, not verified availability or performance. Calls for polling or other operations may also consume API quota. No payment authorized.

## Architecture decision

Reproduce general publicly documented capabilities independently: existing-caption retrieval, queue/checkpoints, duplicate detection, timestamp preservation, caching, multi-format imports and local search. Faster-whisper remains the free fallback for legitimately available audio. None of that proves full source access.

Do not automate GetTheText's website. An API adapter can be considered only after documentation and authorized access are actually available. Build 009 packages the independent caption adapter for a bounded real Windows access test; its cloud test failed. It does not depend on Work's browser exporter.

## Unsent access request

I am building a private, noncommercial Bible-study and accessibility library containing 1,294 cataloged Shepherd's Chapel recordings by Arnold and Dennis Murray. Your site previously provided a transcript for Loj1QDHxH3E. Do you currently offer the Pro API advertised on your pricing page? Your terms say paid plans are not yet on sale. Please provide API documentation, authentication requirements, applicable automated-access terms, quotas (including failed requests and polling), and current monthly price. Is a bounded evaluation or free educational batch possible? We need caption availability results for every supplied video ID, original language/timestamps, and explicit failure statuses. We will not scrape your website, circumvent limits, or publish the full transcripts. This request has NOT been sent.
