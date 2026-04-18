'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { workflowAPI, taskAPI } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

interface WorkflowItem {
    id: number;
    name: string;
    description: string;
    version: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export default function WorkflowsPage() {
    const router = useRouter();
    const { user, isAuthenticated } = useAuthStore();
    const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }
        loadWorkflows();
    }, [isAuthenticated]);

    const loadWorkflows = async () => {
        try {
            const res = await workflowAPI.list();
            setWorkflows(res.data);
        } catch (err) {
            console.error('Failed to load workflows', err);
        }
        setLoading(false);
    };

    const handleCreate = async () => {
        if (!newName.trim()) return;
        try {
            const res = await workflowAPI.create({
                name: newName,
                description: newDesc,
                graph_data: {
                    nodes: [
                        { id: 'start_1', type: 'start', position: { x: 250, y: 50 }, data: { label: '开始' } },
                        { id: 'end_1', type: 'end', position: { x: 250, y: 400 }, data: { label: '结束' } },
                    ],
                    edges: [],
                },
            });
            router.push(`/workflows/${res.data.id}`);
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Create failed');
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('确定要删除此工作流？')) return;
        try {
            await workflowAPI.delete(id);
            setWorkflows((prev) => prev.filter((w) => w.id !== id));
        } catch (err) {
            console.error('Delete failed', err);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 text-white">
            {/* Header */}
            <div className="border-b border-gray-800">
                <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text">
                            KKRPA
                        </h1>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-gray-700">
                            {user?.edition === 'enterprise' ? '🏢 企业版' : '🌐 社区版'}
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-400">👤 {user?.username}</span>
                        <button
                            onClick={() => {
                                useAuthStore.getState().logout();
                                router.push('/login');
                            }}
                            className="text-sm text-gray-500 hover:text-red-400 transition-colors"
                        >
                            退出
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-semibold">我的工作流</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            {user?.edition === 'community'
                                ? `已创建 ${workflows.length}/5 个工作流（社区版限制）`
                                : `共 ${workflows.length} 个工作流`}
                        </p>
                    </div>
                    <button
                        onClick={() => setShowCreate(true)}
                        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-medium
              transition-all shadow-lg shadow-blue-600/20 hover:shadow-blue-600/40"
                    >
                        + 新建工作流
                    </button>
                </div>

                {/* Create dialog */}
                {showCreate && (
                    <div className="mb-6 p-5 bg-gray-900/80 rounded-xl border border-gray-700 space-y-3">
                        <input
                            type="text"
                            placeholder="工作流名称"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-sm outline-none
                focus:ring-2 focus:ring-blue-500"
                            autoFocus
                        />
                        <textarea
                            placeholder="描述（可选）"
                            value={newDesc}
                            onChange={(e) => setNewDesc(e.target.value)}
                            rows={2}
                            className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-sm outline-none
                focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="flex gap-2">
                            <button
                                onClick={handleCreate}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium"
                            >
                                创建
                            </button>
                            <button
                                onClick={() => setShowCreate(false)}
                                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
                            >
                                取消
                            </button>
                        </div>
                    </div>
                )}

                {/* Workflow grid */}
                {loading ? (
                    <div className="flex justify-center py-20">
                        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : workflows.length === 0 ? (
                    <div className="text-center py-20">
                        <div className="text-5xl mb-4">📋</div>
                        <p className="text-gray-400 text-lg">还没有工作流</p>
                        <p className="text-gray-600 text-sm mt-1">点击上方按钮创建你的第一个自动化工作流</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {workflows.map((wf) => (
                            <div
                                key={wf.id}
                                className="group bg-gray-900/60 hover:bg-gray-900/90 border border-gray-800 hover:border-gray-600
                  rounded-xl p-5 cursor-pointer transition-all duration-200"
                                onClick={() => router.push(`/workflows/${wf.id}`)}
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <h3 className="text-base font-semibold text-gray-100 group-hover:text-white">
                                        {wf.name}
                                    </h3>
                                    <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">v{wf.version}</span>
                                </div>
                                <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                                    {wf.description || '无描述'}
                                </p>
                                <div className="flex items-center justify-between text-xs text-gray-600">
                                    <span>{new Date(wf.updated_at).toLocaleString('zh-CN')}</span>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDelete(wf.id);
                                        }}
                                        className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                                    >
                                        🗑 删除
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
