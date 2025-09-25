"""YouTube comment crawler module.

Refactored from procedural code to an object‑oriented, argparse‑driven CLI.

Usage examples:
    Full data:
        python -m src.youtube_crawler \
            --url "https://www.youtube.com/watch?v=xxxx"
    Top N (test mode, e.g. first 10 loaded comments):
        python -m src.youtube_crawler \
            --url "https://www.youtube.com/watch?v=xxxx" \
            --use test --n 10

CLI Arguments:
    --url (str): Required. Target YouTube video URL.
    --use (str): 'fulldata' (default) or 'test'. When 'test', --n is required.
    --n (int): When use=test, keep only the first N comments (load order).
"""

from __future__ import annotations

import argparse
import logging
import random
import time
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Container for crawl result."""

    dataframe: pd.DataFrame
    total_comments: int
    used_comments: int
    truncated: bool


class YouTubeCommentCrawler:
    """Crawler class that collects YouTube comments.

    Encapsulates scrolling / element collection / preprocessing logic.
    """

    COMMENT_XPATH = '//*[@id="content-text"]'
    USERNAME_XPATH = '//*[@id="author-text"]'
    LIKE_XPATH = '//*[contains(@id, "vote-count-middle")]'
    AUTHOR_SEL = (
        "#author-text .yt-simple-endpoint.style-scope." "ytd-comment-view-model"
    )
    TIME_SEL = (
        "#published-time-text .yt-simple-endpoint.style-scope." "ytd-comment-view-model"
    )

    def __init__(
        self,
        url: str,
        headless: bool = False,
        scroll_pause_range=(1.5, 3.0),
        driver: Optional[webdriver.Chrome] = None,
    ) -> None:
        self.url = url
        self.headless = headless
        self.scroll_pause_range = scroll_pause_range
        self.driver = driver or self._create_driver()

    def _create_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            # chromium new headless mode
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    def open(self) -> None:
        self.driver.get(self.url)
        time.sleep(2)  # simple wait; can be replaced with WebDriverWait
        # Trigger comments section lazy load: one page down
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(6)  # wait for dynamic elements
        logger.debug("Opened URL and initiated comments section load")

    def scroll_all(
        self,
        max_idle: int = 2,
        max_scroll: Optional[int] = None,
    ) -> None:
        """Scroll until page height stops increasing or limits are reached.

        Args:
            max_idle: consecutive no-change iterations allowed.
            max_scroll: hard cap on scroll attempts (None = unlimited).
        """
        last_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        idle_count = 0
        scroll_count = 0
        while True:
            if max_scroll is not None and scroll_count >= max_scroll:
                logger.debug("Reached max_scroll=%s", max_scroll)
                break
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            )
            scroll_count += 1
            time.sleep(random.uniform(*self.scroll_pause_range))
            new_height = self.driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            if new_height == last_height:
                idle_count += 1
                if idle_count >= max_idle:
                    logger.debug(
                        "Stopping scroll: idle_count=%s max_idle=%s",
                        idle_count,
                        max_idle,
                    )
                    break
            else:
                idle_count = 0
                last_height = new_height
        logger.info(
            "Scrolling finished: attempts=%s idle_count=%s",
            scroll_count,
            idle_count,
        )

    def collect_elements(self):  # omit type hint for brevity
        comments = self.driver.find_elements(By.XPATH, self.COMMENT_XPATH)
        usernames = self.driver.find_elements(By.XPATH, self.USERNAME_XPATH)
        likes = self.driver.find_elements(By.XPATH, self.LIKE_XPATH)
        times_ = self.driver.find_elements(By.CSS_SELECTOR, self.TIME_SEL)
        logger.debug(
            "Collected counts | comments=%d usernames=%d likes=%d times=%d",
            len(comments),
            len(usernames),
            len(likes),
            len(times_),
        )
        return comments, usernames, likes, times_

    def build_dataframe(self, limit: Optional[int] = None) -> CrawlResult:
        comments, usernames, likes, times_ = self.collect_elements()
        data = {
            "usernames": [user.text for user in usernames],
            "n_likes": [like.text if like.text != "" else "0" for like in likes],
            "times": [tm.text.strip() for tm in times_],
            "comment": [cmt.text for cmt in comments],
        }
        df = pd.DataFrame(data)
        # Preprocess: replace non-Korean characters with space
        df["comment"] = df["comment"].str.replace("[^가-힣]", " ", regex=True)
        total = len(df)
        truncated = False
        if limit is not None and total > limit:
            df = df.iloc[:limit].copy()
            truncated = True
        logger.info(
            "DataFrame built: total=%d used=%d truncated=%s",
            total,
            len(df),
            truncated,
        )
        # Ensure type recognized as DataFrame for type checkers
        assert isinstance(df, pd.DataFrame)
        result_df = df  # alias for clarity
        return CrawlResult(
            result_df,
            total_comments=total,
            used_comments=len(result_df),
            truncated=truncated,
        )

    def run(
        self,
        limit: Optional[int] = None,
        max_scroll: Optional[int] = None,
    ) -> CrawlResult:
        try:
            self.open()
            self.scroll_all(max_scroll=max_scroll)
            return self.build_dataframe(limit=limit)
        finally:
            # Resource cleanup (can be made optional if persistence needed)
            self.driver.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YouTube comment crawler")
    parser.add_argument("--url", required=True, help="Target YouTube video URL")
    parser.add_argument(
        "--use",
        default="fulldata",
        choices=["fulldata", "test"],
        help="Use full dataset or test mode (top N)",
    )
    parser.add_argument("--n", type=int, help="Top N comments when --use test")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument(
        "--max-scroll",
        type=int,
        help="Max scroll attempts (omit for auto stop)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "-o", "--output", help="CSV output path (if set, save crawled comments)"
    )
    parser.add_argument(
        "--log-file", help="Log file path (if set, also write logs to this file)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    limit = None
    if args.use == "test":
        if not args.n:
            raise SystemExit("--use test requires --n <int>")
        limit = args.n

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file))
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="[%(levelname)s] %(message)s",
        handlers=handlers,
        force=True,
    )
    logger.debug("Parsed arguments: %s", args)

    crawler = YouTubeCommentCrawler(url=args.url, headless=args.headless)
    result = crawler.run(limit=limit, max_scroll=args.max_scroll)

    print("\n==== Crawl Summary ====")
    print(f"Total collected comments: {result.total_comments}")
    if result.truncated:
        print(
            (f"Used comments: {result.used_comments} " f"(top {result.used_comments})")
        )
    else:
        print(f"Used comments: {result.used_comments}")
    print(result.dataframe.head(10))  # preview first rows

    if args.output:
        result.dataframe.to_csv(args.output, index=False)
        logger.info("Saved CSV: %s", args.output)

    return result


if __name__ == "__main__":
    main()
