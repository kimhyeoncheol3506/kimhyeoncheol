"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { useState } from "react";
import { generateAction } from "@/app/actions/content";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL, PLATFORMS } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

interface CampaignOpt {
  id: string;
  name: string;
  client: { name: string };
}
interface CandOpt {
  id: string;
  title: string;
  platform: string;
  accountName: string;
  campaignId: string | null;
  suitable: boolean | null;
}

const DEFAULT_TYPES = ["COMMENT", "INFORMATIVE", "SNS_POST", "AD_DISCLOSURE"];

export function GenerateForm({ campaigns, candidates, defaultCampaignId }: { campaigns: CampaignOpt[]; candidates: CandOpt[]; defaultCampaignId?: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(generateAction);
  const [campaignId, setCampaignId] = useState(defaultCampaignId ?? "");
  const e = state.errors ?? {};
  const linked = candidates.filter((c) => c.campaignId === campaignId);
  const others = candidates.filter((c) => c.campaignId === null);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-4" noValidate>
      <FormMessage state={state} />
      <div className="grid gap-4 sm:grid-cols-3">
        <Field label="캠페인" htmlFor="g-campaign" error={e.campaignId} required>
          <select id="g-campaign" name="campaignId" value={campaignId} onChange={(ev) => setCampaignId(ev.target.value)} className="input">
            <option value="">캠페인 선택</option>
            {campaigns.map((c) => (
              <option key={c.id} value={c.id}>{c.client.name} — {c.name}</option>
            ))}
          </select>
        </Field>
        <Field label="연결 게시물 (선택)" htmlFor="g-cand" hint="게시물 문맥에 맞춘 댓글·대댓글 초안에 사용">
          <select id="g-cand" name="candidateId" className="input" disabled={!campaignId}>
            <option value="">연결 안 함 (자체 게시물용)</option>
            {linked.length > 0 && (
              <optgroup label="이 캠페인에 연결된 후보">
                {linked.map((c) => (
                  <option key={c.id} value={c.id}>[{c.platform}] {c.title}{c.suitable === false ? " (부적합)" : ""}</option>
                ))}
              </optgroup>
            )}
            <optgroup label="미연결 후보">
              {others.map((c) => (
                <option key={c.id} value={c.id}>[{c.platform}] {c.title}</option>
              ))}
            </optgroup>
          </select>
        </Field>
        <Field label="게시 플랫폼" htmlFor="g-platform" hint="비우면 연결 게시물 또는 희망 SNS 첫 번째">
          <select id="g-platform" name="platform" className="input">
            <option value="">자동</option>
            {PLATFORMS.map((p) => (
              <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
            ))}
          </select>
        </Field>
      </div>
      <fieldset>
        <legend className="label">생성할 문구 유형 <span className="text-rose-500">*</span></legend>
        <div className="flex flex-wrap gap-2">
          {Object.entries(CONTENT_TYPE_LABEL).map(([k, v]) => (
            <label key={k} className="flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm has-[:checked]:border-brand-500 has-[:checked]:bg-brand-50">
              <input type="checkbox" name="types" value={k} defaultChecked={DEFAULT_TYPES.includes(k)} className="accent-brand-600" />
              {v}
            </label>
          ))}
        </div>
        {e.types && <p className="mt-1 text-xs font-medium text-rose-600">{e.types}</p>}
      </fieldset>
      <p className="text-xs text-slate-500">
        생성 원칙: 광고 표시 포함 · 허위 체험담/가짜 이용자 반응 금지 · 브랜드 제공 정보 외 사실 생성 금지 · 금지 표현 배제. 생성 결과는 안전 필터로 다시 검사되며, 사람의 승인 없이는 실행되지 않습니다.
      </p>
      <div className="flex justify-end">
        <SubmitButton pending={pending} pendingText="생성 중…">문구 생성</SubmitButton>
      </div>
    </form>
  );
}
