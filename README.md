# YERM

youTube Ethics Review Model

## YouTube 댓글 크롤러 사용법

`src/youtube_crawler.py` 스크립트는 특정 YouTube 영상의 댓글과 메타데이터를 수집하여 `data/` 디렉토리에 저장합니다.

생성 파일:

- 댓글: `data/날짜_영상제목.csv`
- 메타데이터 누적: `data/metadata.csv`
- 로그: `logs/crawler_YYYYMMDD.log`

### 1. 환경 준비

필수 패키지 설치:

```bash
pip install -r requirements.txt
```

또는 conda 환경 사용:

```bash
conda env create -f environment.yml
conda activate yerm
```

Chrome 브라우저가 설치되어 있어야 하며 Selenium 4.6+ 는 드라이버를 자동 관리합니다.

### 2. 실행 예시

```bash
python -m src.youtube_crawler --url "https://www.youtube.com/watch?v=M2WTUoy4y6E" --headless --max-scroll 250
```

옵션:

- `--url` (필수): 대상 영상 URL
- `--headless`: 브라우저 창을 띄우지 않는 모드
- `--max-scroll` (기본 300): 스크롤 반복 최대 횟수
- `--sleep-min` / `--sleep-max`: 스크롤 간 랜덤 대기 구간(초)
- `--timeout`: 초기 로딩 타임아웃(초)

### 3. 출력 컬럼

댓글 CSV: `username, comment, like_count, relative_time, comment_clean`

메타데이터 CSV: 실행일(run_date), video_id, video_title, channel_name, publish_date, view_count, like_count, comment_count, comments_file, source_url

### 4. 주의사항

- YouTube DOM 구조가 변경되면 선택자 수정이 필요할 수 있습니다.
- 과도한 요청은 차단을 유발할 수 있으므로 스크롤 간 대기시간을 충분히 두세요.

### 5. 환경 업데이트 방법

`requirements.txt` 또는 `environment.yml` 수정 후:

```bash
conda env update -f environment.yml --prune
```

pip 전용 패키지 추가 시(environment.yml의 pip 섹션에 추가):

```bash
conda env update -f environment.yml
```
