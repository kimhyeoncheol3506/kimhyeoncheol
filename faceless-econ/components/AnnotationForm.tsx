"use client";

import { useState } from "react";
import type { FacelessClass, VideoAnnotation } from "@/lib/types";

const EMPTY = (videoId: string): VideoAnnotation => ({
  videoId,
  updatedAt: "",
  thumbnail: { verified: false, text: "", faceVisible: "unknown", elements: [], contrast: "unknown", layout: "" },
  structure: { verified: false, hook: "", firstInfoSec: null, flow: "", cta: "" },
  visual: { verified: false, style: "", cutsPerMinute: null, subtitleDensity: "unknown", notes: "" },
});

const ELEMENTS = ["차트", "숫자", "화살표", "지도", "표", "인물 사진", "로고", "캐릭터"];

export function AnnotationForm({ videoId, initial, disabled }: { videoId: string; initial: VideoAnnotation | null; disabled: boolean }) {
  const [a, setA] = useState<VideoAnnotation>(initial ?? EMPTY(videoId));
  const [msg, setMsg] = useState("");
  const set = <K extends keyof VideoAnnotation>(k: K, v: VideoAnnotation[K]) => setA((p) => ({ ...p, [k]: v }));

  async function save() {
    setMsg("저장 중…");
    const r = await fetch("/api/annotations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(a) });
    setMsg(r.ok ? "저장했습니다. 새로고침하면 패턴 분석에 반영됩니다." : `저장 실패: ${(await r.json()).error}`);
  }

  const input = "w-full rounded-md border border-neutral-300 px-2 py-1 text-sm disabled:bg-neutral-100";
  return (
    <fieldset disabled={disabled} className="space-y-5">
      {disabled && <p className="rounded-md bg-amber-50 p-2 text-sm text-amber-900">데모 데이터에는 확인 입력을 저장하지 않습니다. 실제 수집 후 사용하세요.</p>}

      <div>
        <label className="flex items-center gap-2 text-sm font-semibold">
          <input type="checkbox" checked={a.thumbnail.verified} onChange={(e) => set("thumbnail", { ...a.thumbnail, verified: e.target.checked })} />
          썸네일을 직접 보고 확인함
        </label>
        <div className="mt-2 grid gap-2 md:grid-cols-2">
          <input className={input} placeholder="썸네일 핵심 문구 (보이는 그대로)" value={a.thumbnail.text} onChange={(e) => set("thumbnail", { ...a.thumbnail, text: e.target.value })} />
          <input className={input} placeholder="배치 (예: 왼쪽 문구 2줄, 오른쪽 차트)" value={a.thumbnail.layout} onChange={(e) => set("thumbnail", { ...a.thumbnail, layout: e.target.value })} />
          <select className={input} value={a.thumbnail.faceVisible} onChange={(e) => set("thumbnail", { ...a.thumbnail, faceVisible: e.target.value as "yes" })}>
            <option value="unknown">얼굴 노출: 미확인</option>
            <option value="yes">얼굴 노출: 있음</option>
            <option value="no">얼굴 노출: 없음</option>
          </select>
          <select className={input} value={a.thumbnail.contrast} onChange={(e) => set("thumbnail", { ...a.thumbnail, contrast: e.target.value as "high" })}>
            <option value="unknown">색상 대비: 미확인</option>
            <option value="high">색상 대비: 높음</option>
            <option value="medium">색상 대비: 보통</option>
            <option value="low">색상 대비: 낮음</option>
          </select>
        </div>
        <div className="mt-2 flex flex-wrap gap-3 text-sm">
          {ELEMENTS.map((el) => (
            <label key={el} className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={a.thumbnail.elements.includes(el)}
                onChange={(e) =>
                  set("thumbnail", { ...a.thumbnail, elements: e.target.checked ? [...a.thumbnail.elements, el] : a.thumbnail.elements.filter((x) => x !== el) })
                }
              />
              {el}
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="flex items-center gap-2 text-sm font-semibold">
          <input type="checkbox" checked={a.structure.verified} onChange={(e) => set("structure", { ...a.structure, verified: e.target.checked })} />
          영상을 직접 시청하고 구성을 확인함
        </label>
        <div className="mt-2 grid gap-2 md:grid-cols-2">
          <textarea className={input} rows={2} placeholder="도입부 문제 제시 방식 (요약, 원문 전사 금지)" value={a.structure.hook} onChange={(e) => set("structure", { ...a.structure, hook: e.target.value })} />
          <input
            className={input}
            type="number"
            placeholder="첫 핵심 정보 등장 시점(초)"
            value={a.structure.firstInfoSec ?? ""}
            onChange={(e) => set("structure", { ...a.structure, firstInfoSec: e.target.value === "" ? null : Number(e.target.value) })}
          />
          <textarea className={input} rows={2} placeholder="흐름: 문제→기대→발견→근거→의미→행동 (요약)" value={a.structure.flow} onChange={(e) => set("structure", { ...a.structure, flow: e.target.value })} />
          <input className={input} placeholder="결론·CTA 방식" value={a.structure.cta} onChange={(e) => set("structure", { ...a.structure, cta: e.target.value })} />
        </div>
      </div>

      <div>
        <label className="flex items-center gap-2 text-sm font-semibold">
          <input type="checkbox" checked={a.visual.verified} onChange={(e) => set("visual", { ...a.visual, verified: e.target.checked })} />
          시각 전달 방식을 직접 확인함
        </label>
        <div className="mt-2 grid gap-2 md:grid-cols-3">
          <input className={input} placeholder="방식 (내레이션+자료/애니메이션/차트…)" value={a.visual.style} onChange={(e) => set("visual", { ...a.visual, style: e.target.value })} />
          <input
            className={input}
            type="number"
            placeholder="분당 화면 전환 수(대략)"
            value={a.visual.cutsPerMinute ?? ""}
            onChange={(e) => set("visual", { ...a.visual, cutsPerMinute: e.target.value === "" ? null : Number(e.target.value) })}
          />
          <select className={input} value={a.visual.subtitleDensity} onChange={(e) => set("visual", { ...a.visual, subtitleDensity: e.target.value as "high" })}>
            <option value="unknown">자막 밀도: 미확인</option>
            <option value="high">자막 밀도: 높음</option>
            <option value="medium">자막 밀도: 보통</option>
            <option value="low">자막 밀도: 낮음</option>
          </select>
          <textarea className={`${input} md:col-span-3`} rows={2} placeholder="차트·표·지도·스크린샷·B-roll 활용 메모" value={a.visual.notes} onChange={(e) => set("visual", { ...a.visual, notes: e.target.value })} />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="font-semibold">영상 페이스리스 판정(직접 확인):</span>
        <select
          className="rounded-md border border-neutral-300 px-2 py-1"
          value={a.faceless?.cls ?? ""}
          onChange={(e) => set("faceless", e.target.value ? { cls: e.target.value as FacelessClass, confirmed: true } : undefined)}
        >
          <option value="">입력 안 함 (자동 추정 유지)</option>
          <option value="A">A 내레이션+자료 화면</option>
          <option value="B">B 애니메이션·모션그래픽</option>
          <option value="C">C 차트·스크린캐스트</option>
          <option value="D">D 진행자·출연자 노출</option>
          <option value="E">E 혼합형</option>
        </select>
      </div>

      <div className="flex items-center gap-3">
        <button type="button" onClick={save} className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">
          확인 내용 저장
        </button>
        <span className="text-sm text-neutral-600">{msg}</span>
      </div>
    </fieldset>
  );
}
