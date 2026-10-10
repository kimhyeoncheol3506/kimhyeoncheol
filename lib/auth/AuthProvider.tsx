"use client";
import { createContext, useContext, useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { authEnabled, supabase } from "./supabase";

type AuthState = { user: User | null; loading: boolean; enabled: boolean; signOut: () => Promise<void> };

const Ctx = createContext<AuthState>({ user: null, loading: true, enabled: false, signOut: async () => {} });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(authEnabled);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => {
      setUser(data.session?.user ?? null);
      setLoading(false);
    });
    const { data } = supabase.auth.onAuthStateChange((_e, session) => setUser(session?.user ?? null));
    return () => data.subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    await supabase?.auth.signOut();
    setUser(null);
  };

  return <Ctx.Provider value={{ user, loading, enabled: authEnabled, signOut }}>{children}</Ctx.Provider>;
}

export const useAuth = () => useContext(Ctx);
