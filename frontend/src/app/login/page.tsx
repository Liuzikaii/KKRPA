'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function LoginPage() {
    const router = useRouter();
    const { setAuth } = useAuthStore();
    const [isRegister, setIsRegister] = useState(false);
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            let res;
            if (isRegister) {
                res = await authAPI.register(form);
            } else {
                res = await authAPI.login({ username: form.username, password: form.password });
            }
            setAuth(res.data.user, res.data.access_token);
            router.push('/workflows');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Authentication failed');
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
            </div>

            <div className="relative w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
                        KKRPA
                    </h1>
                    <p className="text-gray-500 mt-2 text-sm">自动化流程图形化编程平台</p>
                </div>

                {/* Card */}
                <div className="bg-gray-900/80 backdrop-blur-xl border border-gray-800 rounded-2xl p-8 shadow-2xl">
                    <h2 className="text-xl font-semibold text-white mb-6">
                        {isRegister ? '创建账户' : '登录'}
                    </h2>

                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">用户名</label>
                            <input
                                type="text"
                                value={form.username}
                                onChange={(e) => setForm({ ...form, username: e.target.value })}
                                required
                                className="w-full px-4 py-3 bg-gray-800/60 border border-gray-700 rounded-xl text-sm text-white
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-600"
                                placeholder="输入用户名"
                            />
                        </div>

                        {isRegister && (
                            <div>
                                <label className="block text-xs font-medium text-gray-400 mb-1.5">邮箱</label>
                                <input
                                    type="email"
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    required
                                    className="w-full px-4 py-3 bg-gray-800/60 border border-gray-700 rounded-xl text-sm text-white
                    focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-600"
                                    placeholder="your@email.com"
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">密码</label>
                            <input
                                type="password"
                                value={form.password}
                                onChange={(e) => setForm({ ...form, password: e.target.value })}
                                required
                                className="w-full px-4 py-3 bg-gray-800/60 border border-gray-700 rounded-xl text-sm text-white
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-600"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500
                rounded-xl text-sm font-semibold text-white shadow-lg shadow-blue-600/25
                transition-all duration-200 disabled:opacity-50"
                        >
                            {loading ? '处理中...' : isRegister ? '注册' : '登录'}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <button
                            onClick={() => { setIsRegister(!isRegister); setError(''); }}
                            className="text-sm text-gray-400 hover:text-blue-400 transition-colors"
                        >
                            {isRegister ? '已有账户？登录' : '没有账户？注册'}
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-xs text-gray-600 mt-6">
                    KKRPA v0.1.0 · 支持内嵌 Python 的 RPA 平台
                </p>
            </div>
        </div>
    );
}
