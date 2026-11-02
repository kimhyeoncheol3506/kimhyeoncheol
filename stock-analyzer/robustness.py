"""과최적화 방지 검증 (Validation Gate).

"백테스트가 좋다"가 아니라 "그 좋음이 우연이 아니다"를 확인하는 도구 모음.
참고한 공개 방법론:
  - PSR / Deflated Sharpe  (Bailey & López de Prado, 2012/2014)
  - PBO via CSCV            (Bailey, Borwein, López de Prado, Zhu, 2015)
  - CPCV + purge/embargo    (López de Prado, 2018)
  - 워크포워드, 파라미터 안정성, 고원(plateau), 몬테카를로, 국면별 성과, 엣지 감소
영감: ralphtradesz/trading-hub 의 검증 게이트 (합격 기준 아이디어만 참고, 코드는 새로 작성).

사용: validate(close_df, strategy_no) → 검증 결과(dict)
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from quant import COST_ONE_WAY, STRATEGY_NAMES, _hold, run_bt

ANN = math.sqrt(252)
EULER = 0.5772156649

# --------------------------------------------------------------------------- #
# 합격 기준 (Pass / Warn / Fail)
# --------------------------------------------------------------------------- #
MIN_TRADES = 30
MIN_PF, FAIL_PF = 1.2, 1.0
MIN_EFF, FAIL_EFF = 0.5, 0.3
MIN_WIN_PCT, FAIL_WIN_PCT = 60, 40
MIN_WINDOWS = 4
MAX_INSTAB = 0.35
MIN_PLATEAU, MIN_PROFIT_COMBOS = 0.5, 0.25
MIN_DSR, FAIL_DSR = 0.9, 0.5
MAX_PBO_LOSS, FAIL_PBO_LOSS = 0.2, 0.5
MIN_CPCV_POS = 0.6


# --------------------------------------------------------------------------- #
# 통계: PSR / DSR
# --------------------------------------------------------------------------- #
def sharpe_stats(r: pd.Series) -> tuple[float, float, float, int]:
    r = r.dropna()
    n = len(r)
    if n < 10 or r.std() == 0:
        return 0.0, 0.0, 3.0, n
    return float(r.mean() / r.std()), float(stats.skew(r)), float(stats.kurtosis(r, fisher=False)), n


def psr(sr: float, bench: float, n: int, skew: float, kurt: float) -> float:
    """진짜 Sharpe가 bench보다 클 확률 (비정규성·표본길이 보정). sr은 비연율(기간당) Sharpe."""
    if n < 3:
        return float("nan")
    den = 1 - skew * sr + (kurt - 1) / 4 * sr ** 2
    if den <= 0:
        return float("nan")
    return float(stats.norm.cdf((sr - bench) * math.sqrt(n - 1) / math.sqrt(den)))


def expected_max_sr(trials: int, var: float) -> float:
    """아무 능력 없는 전략을 trials번 시도했을 때 우연히 나오는 최대 Sharpe(기간당)의 기대값."""
    if trials <= 1 or var <= 0:
        return 0.0
    return math.sqrt(var) * ((1 - EULER) * stats.norm.ppf(1 - 1 / trials) + EULER * stats.norm.ppf(1 - 1 / (trials * math.e)))


def deflated_sharpe(r: pd.Series, trials: int, trial_sharpes: np.ndarray) -> float:
    sr, sk, ku, n = sharpe_stats(r)
    var = float(np.var(trial_sharpes, ddof=1)) if len(trial_sharpes) > 1 else 0.0
    var = max(var, 1.0 / max(n, 1))   # 표본 Sharpe 추정 잡음보다 작게 잡지 않음
    return psr(sr, expected_max_sr(trials, var), n, sk, ku)


# --------------------------------------------------------------------------- #
# 파라미터화된 전략 (quant.py의 규칙을 파라미터로 일반화)
# --------------------------------------------------------------------------- #
def f_mom(c, v, h, l, p):
    L = p["L"]
    return ((c.shift(21) / c.shift(L) - 1 > 0) & (c / c.shift(max(L // 2, 21)) - 1 > 0)).astype(float)


def f_mr(c, v, h, l, p):
    m, s = c.rolling(p["n"]).mean(), c.rolling(p["n"]).std()
    z = (c - m) / s
    return _hold((z < -p["e"]).to_numpy(), (z >= 0).to_numpy(), c.index)


def f_trend(c, v, h, l, p):
    fast, slow = c.rolling(p["fast"]).mean(), c.rolling(p["slow"]).mean()
    return ((c > slow) & (fast > slow)).astype(float)


def f_rev(c, v, h, l, p):
    r3 = c.pct_change(3)
    z = (r3 - r3.rolling(120).mean()) / r3.rolling(120).std()
    spike = v >= p["vm"] * v.rolling(20).mean().shift(1)
    return ((z <= -p["thr"]) & spike).astype(float).rolling(p["hold"], min_periods=1).max()


def f_brk(c, v, h, l, p):
    hi = h.rolling(p["N"]).max().shift(1)
    lo = l.rolling(p["N2"]).min().shift(1)
    vol_ok = v >= p["vm"] * v.rolling(20).mean().shift(1)
    return _hold(((c > hi) & vol_ok).to_numpy(), (c < lo).to_numpy(), c.index)


STRATS = {
    1: (f_mom, {"L": [126, 189, 252, 315]}),
    2: (f_mr, {"n": [10, 20, 30], "e": [1.0, 1.5, 2.0, 2.5]}),
    5: (f_trend, {"fast": [20, 50, 80], "slow": [100, 150, 200, 250]}),
    13: (f_rev, {"thr": [1.5, 2.0, 2.5], "vm": [1.0, 1.5, 2.0], "hold": [2, 3, 5]}),
    14: (f_brk, {"N": [20, 40, 55, 100], "vm": [1.0, 1.5], "N2": [10, 20, 30]}),
}
DEFAULTS = {1: {"L": 252}, 2: {"n": 20, "e": 1.5}, 5: {"fast": 50, "slow": 200},
            13: {"thr": 2.0, "vm": 1.5, "hold": 3}, 14: {"N": 55, "vm": 1.5, "N2": 20}}


def _configs(grid: dict) -> list[dict]:
    keys = list(grid)
    out = [dict(zip(keys, vals)) for vals in itertools.product(*grid.values())]
    if "fast" in grid:
        out = [c for c in out if c["fast"] < c["slow"]]
    return out


def _neighbors(i: int, cfgs: list[dict], grid: dict) -> list[int]:
    """한 파라미터만 한 칸 이웃으로 바꾼 설정들의 인덱스."""
    res = []
    for k, vals in grid.items():
        j = vals.index(cfgs[i][k])
        for d in (-1, 1):
            if 0 <= j + d < len(vals):
                cand = {**cfgs[i], k: vals[j + d]}
                if cand in cfgs:
                    res.append(cfgs.index(cand))
    return res


def build_matrix(df: pd.DataFrame, strat_no: int) -> tuple[pd.DataFrame, dict[int, pd.Series], list[dict], dict]:
    fn, grid = STRATS[strat_no]
    cfgs = _configs(grid)
    c, v, h, l = df["Close"], df["Volume"], df["High"], df["Low"]
    cols, poss = {}, {}
    for i, p in enumerate(cfgs):
        pos = fn(c, v, h, l, p).fillna(0.0)
        poss[i] = pos
        cols[i] = run_bt(c, pos)
    return pd.DataFrame(cols), poss, cfgs, grid


def _sh(M: pd.DataFrame | pd.Series) -> pd.Series | float:
    sd = M.std()
    return (M.mean() / sd).replace([np.inf, -np.inf], np.nan).fillna(0.0) if isinstance(M, pd.DataFrame) else (
        float(M.mean() / sd) if sd > 0 else 0.0)


# --------------------------------------------------------------------------- #
# 워크포워드
# --------------------------------------------------------------------------- #
@dataclass
class WFResult:
    windows: pd.DataFrame
    oos: pd.Series
    bests: list
    test_index: list
    efficiency: float
    win_pct: float
    instability: float | None


def walk_forward(M: pd.DataFrame, cfgs: list[dict], grid: dict,
                 train: int = 504, test: int = 126) -> WFResult | None:
    T = len(M)
    rows, oos, tidx, start = [], [], [], 0
    while start + train + test <= T:
        tr, te = M.iloc[start:start + train], M.iloc[start + train:start + train + test]
        best = int(_sh(tr).idxmax())
        r = te[best]
        rows.append({"학습 시작": M.index[start], "검증 시작": te.index[0], "검증 끝": te.index[-1], "선택 설정": cfgs[best],
                     "IS Sharpe(연)": float(_sh(tr[best]) * ANN), "OOS Sharpe(연)": float(_sh(r) * ANN),
                     "OOS 수익률": float((1 + r).prod() - 1), "_best": best})
        oos.append(r)
        tidx.append(te.index)
        start += test
    if len(rows) < 2:
        return None
    wdf = pd.DataFrame(rows)
    o = pd.concat(oos)
    mean_is = wdf["IS Sharpe(연)"].mean()
    eff = (_sh(o) * ANN) / mean_is if mean_is > 0 else float("nan")
    win_pct = float((wdf["OOS 수익률"] > 0).mean() * 100)
    inst = []
    for k, vals in grid.items():
        rng = max(vals) - min(vals)
        if rng > 0:
            chosen = [cfgs[b][k] for b in wdf["_best"]]
            inst.append(np.std(chosen) / rng)
    return WFResult(wdf.drop(columns="_best"), o, list(wdf["_best"]), tidx, float(eff), win_pct, float(np.mean(inst)) if inst else None)


# --------------------------------------------------------------------------- #
# PBO (CSCV) / CPCV
# --------------------------------------------------------------------------- #
def pbo_cscv(M: pd.DataFrame, S: int = 8) -> dict | None:
    N, T = M.shape[1], len(M)
    if N < 3 or T < S * 20:
        return None
    blocks = np.array_split(np.arange(T), S)
    logits, losses = [], 0
    combos = list(itertools.combinations(range(S), S // 2))
    for is_idx in combos:
        iset = np.concatenate([blocks[b] for b in is_idx])
        oset = np.concatenate([blocks[b] for b in range(S) if b not in is_idx])
        best = int(_sh(M.iloc[iset]).idxmax())
        osh = _sh(M.iloc[oset])
        rank = osh.rank().iloc[best]          # 1 = 최하위
        w = rank / (N + 1)
        logits.append(math.log(w / (1 - w)))
        losses += float(M.iloc[oset, best].sum()) < 0
    logits = np.array(logits)
    return {"pbo": float((logits <= 0).mean()), "loss": losses / len(combos), "splits": len(combos)}


def cpcv(M: pd.DataFrame, groups: int = 8, k: int = 2, embargo: int = 5) -> dict | None:
    T = len(M)
    if M.shape[1] < 2 or T < groups * 40:
        return None
    b = np.array_split(np.arange(T), groups)
    out = []
    for test_g in itertools.combinations(range(groups), k):
        test = np.concatenate([b[g] for g in test_g])
        banned = set()
        for g in test_g:
            lo, hi = b[g][0], b[g][-1]
            banned.update(range(max(0, lo - embargo), min(T, hi + embargo + 1)))  # 퍼지 + 엠바고
        train = np.array([i for i in range(T) if i not in banned])
        best = int(_sh(M.iloc[train]).idxmax())
        out.append(float(_sh(M.iloc[test, best]) * ANN))
    a = np.array(out)
    return {"paths": len(a), "pos_share": float((a > 0).mean()), "median": float(np.median(a)), "p10": float(np.percentile(a, 10))}


# --------------------------------------------------------------------------- #
# 보조: 고원 · 몬테카를로 · 엣지감소 · 국면 · 거래 추출
# --------------------------------------------------------------------------- #
def plateau(M: pd.DataFrame, cfgs: list[dict], grid: dict) -> tuple[float, int, float]:
    sh = _sh(M)
    best = int(sh.idxmax())
    nb = _neighbors(best, cfgs, grid)
    share = float(np.mean([sh[j] > 0 for j in nb])) if nb else float("nan")
    return share, len(nb), float((sh > 0).mean())


def monte_carlo(r: pd.Series, sims: int = 1000, block: int = 10, seed: int = 0) -> dict:
    x, n = r.to_numpy(), len(r)
    rng = np.random.default_rng(seed)
    tot, mdd = np.empty(sims), np.empty(sims)
    nb = math.ceil(n / block)
    for s in range(sims):
        st = rng.integers(0, max(n - block, 1), nb)
        path = np.concatenate([x[i:i + block] for i in st])[:n]
        eq = np.cumprod(1 + path)
        tot[s] = eq[-1] - 1
        mdd[s] = (eq / np.maximum.accumulate(eq) - 1).min()
    return {"loss_prob": float((tot < 0).mean()), "ret_p5": float(np.percentile(tot, 5)), "ret_p50": float(np.median(tot)),
            "ret_p95": float(np.percentile(tot, 95)), "mdd_p50": float(np.median(mdd)), "mdd_p95_worst": float(np.percentile(mdd, 5))}


def extract_trades(sr: pd.Series, pos: pd.Series) -> pd.Series:
    mask = (pos.shift(1).fillna(0) == 1) | (pos.diff().abs().fillna(0) > 0)
    grp = (mask != mask.shift()).cumsum()
    t = sr[mask].groupby(grp[mask]).apply(lambda x: (1 + x).prod() - 1)
    return t.reset_index(drop=True)


def trade_stats(t: pd.Series) -> dict:
    if len(t) == 0:
        return {"n": 0, "pf": float("nan"), "win": float("nan"), "avg": float("nan")}
    gp, gl = t[t > 0].sum(), -t[t < 0].sum()
    return {"n": len(t), "pf": float(gp / gl) if gl > 0 else float("inf"), "win": float((t > 0).mean()), "avg": float(t.mean())}


def edge_decay(t: pd.Series) -> dict | None:
    if len(t) < 9:
        return None
    k = len(t) // 3
    res = stats.linregress(np.arange(len(t)), t.to_numpy())
    return {"early": float(t.iloc[:k].mean()), "late": float(t.iloc[-k:].mean()), "t": float(res.slope / res.stderr) if res.stderr > 0 else 0.0}


def regime_table(c: pd.Series, oos: pd.Series) -> pd.DataFrame:
    """OOS 일수익을 시장 국면별로 분해 (국면은 전일까지의 정보로 판정)."""
    chg = c.diff().abs()
    er = (c - c.shift(20)).abs() / chg.rolling(20).sum()
    vol = c.pct_change().rolling(20).std()
    vrank = vol.rolling(250, min_periods=60).rank(pct=True)
    lab = pd.DataFrame({
        "추세": np.where(er.shift(1) >= 0.5, "추세장", np.where(er.shift(1) <= 0.25, "횡보장", "혼합")),
        "변동성": np.where(vrank.shift(1) >= 0.67, "고변동", np.where(vrank.shift(1) <= 0.33, "저변동", "보통")),
        "방향": np.where(c.pct_change(20).shift(1) >= 0, "20일 상승", "20일 하락"),
    }, index=c.index).reindex(oos.index)
    rows = []
    for col in lab.columns:
        for name, idx in lab.groupby(col).groups.items():
            r = oos.loc[idx]
            rows.append({"구분": col, "국면": name, "일수": len(r), "누적수익률": float((1 + r).prod() - 1),
                         "연환산 Sharpe": float(_sh(r) * ANN) if len(r) > 20 else np.nan})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# 종합 검증
# --------------------------------------------------------------------------- #
def _grade(v, ok, bad, higher=True):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "Warn"
    if higher:
        return "Pass" if v >= ok else "Fail" if v < bad else "Warn"
    return "Pass" if v <= ok else "Fail" if v >= bad else "Warn"


def _pool(dfs: dict, strat_no: int):
    mats, poss_all = {}, {}
    cfgs = grid = None
    for sym, df in dfs.items():
        df = df.dropna(subset=["Close"])
        M, poss, cfgs, grid = build_matrix(df, strat_no)
        mats[sym], poss_all[sym] = M, poss
    union = sorted(set().union(*[m.index for m in mats.values()]))
    pooled = sum(m.reindex(union).fillna(0.0) for m in mats.values()) / len(mats)
    return pooled, mats, poss_all, cfgs, grid


def validate(data, strat_no: int, train: int = 504, test: int = 126) -> dict:
    """data: 종목 DataFrame 하나 또는 {심볼: DataFrame}. 여러 종목이면 설정별 수익률을 동일가중으로 합쳐
    설정 선택(워크포워드·PBO·CPCV)을 하고, 거래는 종목별로 모아 표본을 늘린다."""
    if strat_no not in STRATS:
        raise ValueError(f"검증 가능 전략: {', '.join(f'{k}.{STRATEGY_NAMES[k]}' for k in STRATS)}")
    dfs = data if isinstance(data, dict) else {"단일": data}
    dfs = {k: v for k, v in dfs.items() if len(v.dropna(subset=["Close"])) >= train + 2 * test + 260}
    if not dfs:
        raise ValueError(f"데이터 부족 (종목당 최소 {train + 2 * test + 260}봉, 5년 데이터 권장)")
    M, mats, poss_all, cfgs, grid = _pool(dfs, strat_no)
    trials = len(cfgs)
    wf = walk_forward(M, cfgs, grid, train, test)
    if wf is None:
        raise ValueError("워크포워드 윈도우가 부족합니다.")

    oos = wf.oos
    pieces = []
    for sym in dfs:
        sr_parts, pos_parts = [], []
        for best, ti in zip(wf.bests, wf.test_index):
            sr_parts.append(mats[sym][best].reindex(ti).fillna(0.0))
            pos_parts.append(poss_all[sym][best].reindex(ti).fillna(0.0))
        pieces.append(extract_trades(pd.concat(sr_parts), pd.concat(pos_parts)))
    trades = pd.concat(pieces, ignore_index=True)
    ts = trade_stats(trades)
    trial_sh = _sh(M).to_numpy()
    dsr = deflated_sharpe(oos, trials, trial_sh)
    sr, sk, ku, n = sharpe_stats(oos)
    pl_share, n_nb, prof_combo = plateau(M, cfgs, grid)
    pb = pbo_cscv(M)
    cp = cpcv(M)
    mc = monte_carlo(oos)
    decay = edge_decay(trades)
    rets = pd.DataFrame({k: v["Close"].pct_change() for k, v in dfs.items()}).reindex(M.index).fillna(0.0).mean(axis=1)
    c = (1 + rets).cumprod()
    bh = rets.loc[oos.index]

    n_win = len(wf.windows)
    ck = []
    g = _grade(ts["n"], MIN_TRADES, 15)
    ck.append(("표본(OOS 거래 수)", g, f"{ts['n']}회 ({len(dfs)}종목 합산, 기준 {MIN_TRADES}회 이상)"))
    g = _grade(ts["pf"], MIN_PF, FAIL_PF)
    ck.append(("수익 팩터(OOS)", g, f"PF {min(ts['pf'], 99):.2f}, 승률 {ts['win'] * 100:.0f}%, 거래당 {ts['avg'] * 100:+.2f}% (기준 PF ≥{MIN_PF})" if ts["n"] else "거래 없음"))
    ck.append(("워크포워드 효율", _grade(wf.efficiency, MIN_EFF, FAIL_EFF),
               f"OOS Sharpe / IS Sharpe = {wf.efficiency:.2f} (≥{MIN_EFF}; 학습 때의 성과가 검증에서 얼마나 유지되는가)"))
    ck.append(("윈도우 일관성", "Warn" if n_win < MIN_WINDOWS else _grade(wf.win_pct, MIN_WIN_PCT, FAIL_WIN_PCT),
               f"{n_win}개 윈도우 중 {wf.win_pct:.0f}% 수익 (≥{MIN_WIN_PCT}%, 윈도우 {MIN_WINDOWS}개 이상 필요)"))
    ck.append(("파라미터 안정성", _grade(wf.instability, MAX_INSTAB, 0.6, higher=False),
               f"선택 파라미터 불안정도 {wf.instability:.2f} (≤{MAX_INSTAB}; 높으면 윈도우마다 최적값이 널뜀)" if wf.instability is not None else "N/A"))
    ck.append(("고원(plateau)", _grade(pl_share, MIN_PLATEAU, 0.25),
               f"최적 설정의 이웃 {n_nb}개 중 {pl_share * 100:.0f}% 수익 (≥{MIN_PLATEAU * 100:.0f}%; 뾰족한 봉우리면 과최적화)" if n_nb else "이웃 없음"))
    ck.append(("수익 조합 비율", _grade(prof_combo, MIN_PROFIT_COMBOS, 0.1),
               f"전체 {trials}개 설정 중 {prof_combo * 100:.0f}%가 수익 (≥{MIN_PROFIT_COMBOS * 100:.0f}%)"))
    ck.append(("Sharpe 디플레이션(DSR)", _grade(dsr, MIN_DSR, FAIL_DSR),
               f"{trials}개 설정을 시도한 점을 감안해도 우연이 아닐 확률 {dsr * 100:.0f}% (≥{MIN_DSR * 100:.0f}%)"))
    if pb:
        g_pbo = _grade(pb["loss"], MAX_PBO_LOSS, FAIL_PBO_LOSS, higher=False)
        if g_pbo == "Pass" and pb["pbo"] > 0.5:
            g_pbo = "Warn"   # 손실은 안 나도 학습 1등이 미지 구간에서 중앙값 아래면 순위 선택이 의미 없다는 뜻
        ck.append(("과최적화 확률(PBO/CSCV)", g_pbo,
                   f"학습 1등이 미지 구간에서 손실 난 비율 {pb['loss'] * 100:.0f}% (≤{MAX_PBO_LOSS * 100:.0f}%), 중앙값 아래로 떨어진 비율(PBO) {pb['pbo'] * 100:.0f}%, {pb['splits']}개 분할"))
    if cp:
        ck.append(("CPCV 경로", "Pass" if cp["pos_share"] >= MIN_CPCV_POS and cp["median"] > 0 else
                   "Fail" if cp["pos_share"] < 0.4 or cp["median"] <= 0 else "Warn",
                   f"{cp['paths']}개 조합 경로 중 {cp['pos_share'] * 100:.0f}% 수익, 중앙 Sharpe {cp['median']:.2f}, 하위10% {cp['p10']:.2f} (퍼지+엠바고 적용)"))

    fails = [x for x in ck if x[1] == "Fail"]
    warns = [x for x in ck if x[1] == "Warn"]
    sample_dep = {"표본(OOS 거래 수)", "Sharpe 디플레이션(DSR)", "윈도우 일관성", "워크포워드 효율"}
    status = "Fail" if fails else "Warn" if warns else "Pass"
    needs_more = bool(fails) and all(x[0] in sample_dep for x in fails) and ts["n"] < MIN_TRADES and (ts["pf"] == ts["pf"] and ts["pf"] >= MIN_PF)
    verdict = {"Pass": "✅ 통과", "Warn": "🟡 의심", "Fail": "❌ 불합격"}[status]
    if needs_more:
        verdict = "⏳ 표본 부족 (엣지는 보이나 거래 수가 모자라 결론 불가)"

    return {
        "strategy": f"{strat_no}. {STRATEGY_NAMES[strat_no]}", "n_symbols": len(dfs), "status": status, "verdict": verdict, "checks": ck,
        "trials": trials, "windows": wf.windows, "oos": oos, "bh": bh,
        "oos_equity": (1 + oos).cumprod(), "bh_equity": (1 + bh).cumprod(),
        "oos_perf": {"CAGR": float((1 + oos).prod() ** (252 / len(oos)) - 1), "Sharpe(연)": float(sr * ANN),
                     "MDD": float(((1 + oos).cumprod() / (1 + oos).cumprod().cummax() - 1).min()),
                     "B&H CAGR": float((1 + bh).prod() ** (252 / len(bh)) - 1), "B&H Sharpe(연)": float(_sh(bh) * ANN)},
        "mc": mc, "decay": decay, "regimes": regime_table(c, oos), "trades": trades, "pbo": pb, "cpcv": cp,
        "grid": grid, "default": DEFAULTS.get(strat_no),
    }


def validate_trades(rets: pd.Series | list, trials: int = 1, trial_sharpes: list | None = None,
                    min_trades: int = MIN_TRADES) -> dict:
    """거래 단위 수익률(눌림목 전략 등)의 간이 검증: PSR/DSR, 엣지 감소, 몬테카를로.
    trials: 이 전략을 만들기까지 시도한 설정/버전 수(많을수록 디플레이션이 커짐)."""
    t = pd.Series(list(rets), dtype=float).dropna().reset_index(drop=True)
    st = trade_stats(t)
    sr, sk, ku, n = sharpe_stats(t)
    ts = np.array(trial_sharpes) if trial_sharpes else np.array([sr])
    dsr = deflated_sharpe(t, max(trials, 1), ts) if n >= 10 else float("nan")
    decay = edge_decay(t)
    mc = monte_carlo(t, block=3) if n >= 10 else None
    ck = [("표본(거래 수)", _grade(st["n"], min_trades, 15), f"{st['n']}회 (기준 {min_trades}회 이상)"),
          ("수익 팩터", _grade(st["pf"], MIN_PF, FAIL_PF) if st["n"] else "Warn", f"PF {st['pf']:.2f}, 승률 {st['win'] * 100:.0f}%, 거래당 {st['avg'] * 100:+.2f}%" if st["n"] else "거래 없음"),
          ("Sharpe 디플레이션(DSR)", _grade(dsr, MIN_DSR, FAIL_DSR), f"시도 횟수 {trials}회 감안 시 우연이 아닐 확률 {dsr * 100:.0f}% (≥{MIN_DSR * 100:.0f}%)" if dsr == dsr else "표본 부족")]
    if decay:
        ck.append(("엣지 감소", "Fail" if decay["t"] < -2 else "Warn" if decay["t"] < -1 else "Pass",
                   f"앞 1/3 거래당 {decay['early'] * 100:+.2f}% → 뒤 1/3 {decay['late'] * 100:+.2f}% (추세 t={decay['t']:.2f}; 음수면 엣지가 사라지는 중)"))
    status = "Fail" if any(x[1] == "Fail" for x in ck) else "Warn" if any(x[1] == "Warn" for x in ck) else "Pass"
    return {"status": status, "verdict": {"Pass": "✅ 통과", "Warn": "🟡 의심", "Fail": "❌ 불합격"}[status], "checks": ck, "mc": mc, "stats": st}
