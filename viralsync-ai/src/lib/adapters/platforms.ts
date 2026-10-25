import type { PlatformKey } from "@prisma/client";
import { BaseAdapter } from "./base";
import type { PlatformAdapter } from "./types";

export class ThreadsAdapter extends BaseAdapter {
  readonly key = "THREADS" as const;
  readonly name = "Threads";
  readonly requiredEnv = ["THREADS_APP_ID", "THREADS_APP_SECRET"];
  readonly docsUrl = "https://developers.facebook.com/docs/threads";
  readonly apiNotes =
    "Threads API: 인증한 본인 계정에 텍스트·이미지 게시(threads_content_publish). 이미지는 공개 https 주소에 있어야 함. 24시간 250건 제한. ‘스레드 바로 올리기’ 화면에서 실제 게시 지원.";
}

export class InstagramAdapter extends BaseAdapter {
  readonly key = "INSTAGRAM" as const;
  readonly name = "Instagram";
  readonly requiredEnv = ["INSTAGRAM_APP_ID", "INSTAGRAM_APP_SECRET"];
  readonly docsUrl = "https://developers.facebook.com/docs/instagram-platform";
  readonly apiNotes =
    "Instagram Graph API: 비즈니스/크리에이터 계정의 자체 게시물 발행·자체 게시물 댓글 관리 범위. 타인 게시물 댓글 자동 작성은 지원 대상이 아님. 앱 검수 필요.";
}

export class TikTokAdapter extends BaseAdapter {
  readonly key = "TIKTOK" as const;
  readonly name = "TikTok";
  readonly requiredEnv = ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"];
  readonly docsUrl = "https://developers.tiktok.com/doc/content-posting-api-get-started";
  readonly apiNotes = "Content Posting API: 인증된 사용자 본인 계정으로 영상 게시. 앱 심사 전에는 비공개 게시로 제한될 수 있음. 댓글 작성 API 없음.";
}

export class XAdapter extends BaseAdapter {
  readonly key = "X" as const;
  readonly name = "X";
  readonly requiredEnv = ["X_API_KEY", "X_API_SECRET"];
  readonly docsUrl = "https://docs.x.com/x-api/introduction";
  readonly apiNotes = "X API v2: 인증 계정의 게시물·답글 작성. 요금제별 호출 한도가 있으며 자동화 규칙(스팸·중복 금지)을 준수해야 함.";
}

export class FacebookAdapter extends BaseAdapter {
  readonly key = "FACEBOOK" as const;
  readonly name = "Facebook";
  readonly requiredEnv = ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET"];
  readonly docsUrl = "https://developers.facebook.com/docs/pages-api";
  readonly apiNotes = "Pages API: 관리 권한이 있는 페이지에 게시. 브랜디드 콘텐츠는 유료 파트너십 표시 도구 사용 권장. 앱 검수 필요.";
}

export class YouTubeAdapter extends BaseAdapter {
  readonly key = "YOUTUBE" as const;
  readonly name = "YouTube";
  readonly requiredEnv = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET"];
  readonly docsUrl = "https://developers.google.com/youtube/v3";
  readonly apiNotes = "YouTube Data API v3: OAuth 인증 채널의 영상 업로드·메타데이터·댓글 작성. 일일 쿼터 제한, 유료 PPL 은 업로드 시 '유료 프로모션 포함' 표시 필요.";
}

export class BlogAdapter extends BaseAdapter {
  readonly key = "BLOG" as const;
  readonly name = "블로그";
  readonly requiredEnv = ["BLOG_API_KEY"];
  readonly docsUrl = "https://developer.wordpress.org/rest-api/";
  readonly apiNotes = "블로그 서비스마다 공식 API 제공 여부가 다름 (예: WordPress REST API). 국내 포털 블로그는 공식 글쓰기 API 제공 여부를 개별 확인해야 함.";
}

const ADAPTERS: Record<PlatformKey, PlatformAdapter> = {
  THREADS: new ThreadsAdapter(),
  INSTAGRAM: new InstagramAdapter(),
  TIKTOK: new TikTokAdapter(),
  X: new XAdapter(),
  FACEBOOK: new FacebookAdapter(),
  YOUTUBE: new YouTubeAdapter(),
  BLOG: new BlogAdapter(),
};

export function getAdapter(key: PlatformKey): PlatformAdapter {
  return ADAPTERS[key];
}

export function allAdapters(): PlatformAdapter[] {
  return Object.values(ADAPTERS);
}
