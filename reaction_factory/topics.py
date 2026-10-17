"""'터지는 주제 100개' 데이터셋: 조회, 카테고리 랭킹, 자동 매칭, 실데이터 재보정."""
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import DATA_DIR
from utils import console, load_json, save_json

TOPIC_FILE = DATA_DIR / "topics.json"
GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo={geo}"


@dataclass
class Topic:
    id: str
    rank: int
    category: str
    category_name: str
    category_rank: int
    title_ko: str
    keywords_en: list[str]
    keywords_ko: list[str]
    hook_angle: str
    trend_score: float

    @property
    def search_queries(self) -> list[str]:
        return self.keywords_en + self.keywords_ko[:1]


class TopicDB:
    def __init__(self, path: Path = TOPIC_FILE):
        self.path = path
        self.raw = load_json(path)
        self.categories: dict[str, str] = self.raw["categories"]
        self.topics = [Topic(**t) for t in self.raw["topics"]]
        self._rerank()

    # ---------- 조회 ----------
    def get(self, key: str) -> Topic | None:
        """id(T001) 또는 전체 순위 번호(1~100) 또는 제목 일부로 찾기."""
        key = key.strip()
        if key.isdigit():
            return next((t for t in self.topics if t.rank == int(key)), None)
        for t in self.topics:
            if t.id.lower() == key.lower():
                return t
        return next((t for t in self.topics if key in t.title_ko), None)

    def top(self, n: int = 20, category: str | None = None) -> list[Topic]:
        items = [t for t in self.topics if category in (None, t.category)]
        return sorted(items, key=lambda t: t.rank)[:n]

    def by_category(self) -> dict[str, list[Topic]]:
        out: dict[str, list[Topic]] = {k: [] for k in self.categories}
        for t in sorted(self.topics, key=lambda t: t.category_rank):
            out[t.category].append(t)
        return out

    # ---------- 자동 매칭 ----------
    def match(self, text: str, n: int = 5) -> list[tuple[Topic, float]]:
        """검색어/영상 제목과 가장 잘 맞는 주제. 키워드 겹침 + trend_score 가중."""
        words = set(_tokens(text))
        scored = []
        for t in self.topics:
            vocab = set(_tokens(" ".join(t.keywords_en + t.keywords_ko + [t.title_ko])))
            overlap = len(words & vocab)
            if overlap:
                scored.append((t, overlap * 10 + t.trend_score / 10))
        scored.sort(key=lambda x: -x[1])
        return scored[:n]

    def auto_pick(self, use_trends: bool = True, exploration: float = 0.25) -> Topic:
        """'딸깍' 모드용 주제 자동 선택.

        1) 구글 트렌드(한국) 실시간 검색어와 겹치는 주제가 있으면 우선.
        2) 없으면 상위 20개 중 trend_score 가중 랜덤(같은 주제만 반복하지 않도록 약간의 탐색).
        """
        if use_trends:
            trends = fetch_google_trends()
            for kw in trends:
                hits = self.match(kw, n=1)
                if hits and hits[0][1] >= 15:
                    console.print(f"[cyan]트렌드 키워드 '{kw}' → 주제 '{hits[0][0].title_ko}' 매칭[/]")
                    return hits[0][0]
        pool = self.top(20)
        if random.random() < exploration:
            pool = self.top(60)
        weights = [max(t.trend_score, 1) ** 2 for t in pool]
        return random.choices(pool, weights=weights, k=1)[0]

    # ---------- 실데이터 재보정 ----------
    def recalibrate(self, topic: Topic, videos: list[dict]) -> float:
        """탐색 결과의 '시간당 조회수'로 trend_score 를 이동평균 업데이트."""
        if not videos:
            return topic.trend_score
        top = sorted(videos, key=lambda v: -v.get("views_per_hour", 0))[:5]
        vph = sum(v.get("views_per_hour", 0) for v in top) / len(top)
        # 시간당 1만 회 ≈ 100점 이 되도록 로그 스케일 변환
        import math

        observed = max(0.0, min(100.0, 25 * math.log10(max(vph, 1))))
        topic.trend_score = round(topic.trend_score * 0.6 + observed * 0.4, 1)
        self._rerank()
        return topic.trend_score

    def save(self) -> None:
        self.raw["topics"] = [t.__dict__ for t in sorted(self.topics, key=lambda t: t.rank)]
        save_json(self.path, self.raw)

    def _rerank(self) -> None:
        for r, t in enumerate(sorted(self.topics, key=lambda t: -t.trend_score), 1):
            t.rank = r
        counter: dict[str, int] = {}
        for t in sorted(self.topics, key=lambda t: t.rank):
            counter[t.category] = counter.get(t.category, 0) + 1
            t.category_rank = counter[t.category]


def _tokens(text: str) -> list[str]:
    stop = {"reaction", "reacts", "first", "time", "korean", "korea", "foreigners", "외국인", "반응", "해외반응", "the", "to", "in", "try"}
    return [w for w in re.findall(r"[a-z0-9]+|[가-힣]{2,}", text.lower()) if w not in stop]


def fetch_google_trends(geo: str = "KR", timeout: float = 8.0) -> list[str]:
    """구글 트렌드 일간 급상승 검색어(RSS). 실패하면 빈 리스트."""
    try:
        r = requests.get(GOOGLE_TRENDS_RSS.format(geo=geo), timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        return [item.title.get_text(strip=True) for item in soup.find_all("item") if item.title]
    except Exception:
        return []
