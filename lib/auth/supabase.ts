import { createClient, type SupabaseClient } from "@supabase/supabase-js";

// Supabase 주소와 키가 설정되어 있으면 회원가입/로그인이 켜집니다.
// 설정이 없으면 '테스트 모드'로 로그인 없이 이용할 수 있습니다.
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const authEnabled = Boolean(url && key);
export const supabase: SupabaseClient | null = authEnabled ? createClient(url!, key!) : null;
