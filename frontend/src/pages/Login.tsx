import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Server, Lock, User as UserIcon, ShieldCheck, ArrowRight, Info } from 'lucide-react';
import { useAuth, getRoleSlug } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setErrorMsg('Please enter both username and password.');
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);
    try {
      const userProfile = await login(username.trim(), password);
      const targetSlug = getRoleSlug(userProfile?.role);
      navigate(`/dashboard/${targetSlug}`, { replace: true });
    } catch (err: any) {
      setErrorMsg(
        err.response?.data?.detail || 'Invalid username or password. Please verify your PostgreSQL credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070B12] flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Banner */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center mx-auto shadow-lg shadow-emerald-950/50">
            <Server className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">FreshMart</h2>
          <p className="text-xs text-emerald-400 font-medium tracking-wider uppercase">
            Agentic Analytics Platform
          </p>
          <p className="text-xs text-slate-400">
            Secure multi-agent natural language intelligence powered by MCP
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <span className="text-sm font-semibold text-white">Enterprise Sign In</span>
            <Badge variant="emerald" size="sm">PostgreSQL RBAC</Badge>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Username</label>
              <div className="relative">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  placeholder="e.g. ceo, sales.manager, hr.manager, finance.manager"
                  className="w-full bg-[#080C14] border border-slate-700/80 focus:border-emerald-500 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/40"
                />
                <UserIcon className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full bg-[#080C14] border border-slate-700/80 focus:border-emerald-500 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/40"
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full"
              isLoading={isLoading}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In to Analytics
            </Button>
          </form>

          {/* Secure Hackathon Evaluation Info (No auto-fill / No bypass) */}
          <div className="pt-4 border-t border-slate-800/80">
            <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400">
              <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-300 block mb-0.5">Hackathon Demo Accounts</span>
                <span>Usernames: <code className="text-emerald-300">ceo</code>, <code className="text-emerald-300">sales.manager</code>, <code className="text-emerald-300">hr.manager</code>, <code className="text-emerald-300">finance.manager</code>, <code className="text-emerald-300">inventory.manager</code>, <code className="text-emerald-300">erp.manager</code>. Standard format: <code className="text-slate-300">&lt;Role&gt;Password123!</code></span>
              </div>
            </div>
          </div>
        </div>

        {/* Security Footer Note */}
        <div className="text-center text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500/80" />
          <span>Single-Company FreshMart Scope — Bcrypt Hashed PostgreSQL Authentication</span>
        </div>
      </div>
    </div>
  );
};
