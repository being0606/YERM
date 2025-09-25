# YERM

YouTube Ethics Review Model

## 1. Overview

This repository currently provides a YouTube comment crawler (`src/youtube_crawler.py`).
It retrieves comments for a single public video, performs a simple text clean-up
(retain Korean characters only), and can optionally save results to CSV and log to a file.

> NOTE: Earlier documentation mentioned collecting full video metadata; the current
> implementation focuses on comments only. Metadata aggregation can be added later.

## 2. Environment Setup

Install required packages (pip):

```bash
pip install -r requirements.txt
```

Or create the Conda environment:

```bash
conda env create -f environment.yml
conda activate yerm
```

Requirements:

- Chrome browser installed (Selenium 4.6+ manages ChromeDriver automatically)
- Stable network connection

## 3. Direct CLI Usage (Python Module)

Basic example (headless full crawl with scroll limit):

```bash
python -m src.youtube_crawler \
	--url "https://www.youtube.com/watch?v=M2WTUoy4y6E" \
	--headless \
	--max-scroll 250 \
	-o data/comments.csv \
	--log-file logs/crawler.log
```

### 3.1 Command Line Options

| Option                  | Required          | Description                                        |
| ----------------------- | ----------------- | -------------------------------------------------- |
| `--url`                 | Yes               | Target YouTube video URL                           |
| `--use {fulldata,test}` | No                | Full dataset (default) or test mode (top N)        |
| `--n N`                 | When `--use test` | Keep only first N loaded comments                  |
| `--headless`            | No                | Run Chrome in headless mode                        |
| `--max-scroll N`        | No                | Hard cap on scroll attempts (auto-stop if omitted) |
| `--log-level LEVEL`     | No                | Logging verbosity (DEBUG/INFO/...) default INFO    |
| `-o, --output PATH`     | No                | Save comments to CSV at PATH                       |
| `--log-file PATH`       | No                | Also write logs to PATH                            |

### 3.2 Test Mode Example

Grab only the first 20 comments (quick verification):

```bash
python -m src.youtube_crawler \
	--url "https://www.youtube.com/watch?v=VIDEO_ID" \
	--use test --n 20 --headless
```

## 4. Using `scripts/run_crawler.sh`

A convenience script is provided at the project root: `scripts/run_crawler.sh`.

1. Make it executable (first time only):

```bash
chmod +x scripts/run_crawler.sh
```

2. Open the script and set `VIDEO_URL` near the top (or leave the example).
3. Run:

```bash
./scripts/run_crawler.sh
```

```bash
chmod +x scripts/run_crawler.sh
```

```bash
./scripts/run_crawler.sh
```

What it does:

- Creates `data/` and `logs/` if missing
- Generates timestamped CSV `data/comments_YYYYMMDD_HHMMSS.csv`
- Generates log file `logs/crawler_YYYYMMDD_HHMMSS.log`
- Executes a full headless crawl (default block)

Test crawl: Uncomment the "Test Crawl" example block inside the script to limit to top N comments.

````

What it does:

- Creates `data/` and `logs/` if missing
- Generates timestamped CSV `data/comments_YYYYMMDD_HHMMSS.csv`
- Generates log file `logs/crawler_YYYYMMDD_HHMMSS.log`
- Executes a full headless crawl (default block)

Test crawl: Uncomment the "Test Crawl" example block inside the script to limit to top N comments.

## 5. Output Schema

When saving (`-o/--output`), the CSV columns are:

| Column      | Description                                                |
| ----------- | ---------------------------------------------------------- |
| `usernames` | Comment author display names                               |
| `n_likes`   | Like counts (string, '0' if empty)                         |
| `times`     | Relative published time text (e.g., '2 days ago')          |
| `comment`   | Cleaned comment text (non-Korean chars replaced by spaces) |

## 6. Notes / Caveats

- YouTube DOM / CSS selectors can change; update constants in `YouTubeCommentCrawler` if breakage occurs.
- Aggressive rapid scrolling can trigger temporary rate-limiting; the crawler includes random pauses.
- Headless mode may sometimes load fewer elements than a visible session; retry without `--headless` if counts seem low.
- Internationalization: current cleaning step keeps only Korean characters; adapt the regex for multilingual needs.

## 7. Extending / Roadmap Ideas

Potential enhancements (not yet implemented):

- Video/channel metadata enrichment
- Reply thread expansion
- Proxy / rotating user-agent support
- Retry & backoff strategy abstraction
- Batch crawl from a list of video IDs / URLs

## 8. Updating the Environment

After editing `environment.yml`:

```bash
conda env update -f environment.yml --prune
````

If adding pip-only packages (in the pip subsection of `environment.yml`):

```bash
conda env update -f environment.yml
```

---

Feel free to open issues or extend the crawler class for additional functionality.
