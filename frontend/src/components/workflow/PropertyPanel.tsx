'use client';

import { useWorkflowStore } from '@/lib/store';
import dynamic from 'next/dynamic';

// Dynamically import Monaco Editor (no SSR)
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function PropertyPanel() {
    const { selectedNode, updateNodeData } = useWorkflowStore();

    if (!selectedNode) {
        return (
            <div className="w-80 bg-gray-900/80 backdrop-blur-xl border-l border-gray-700/50 flex items-center justify-center p-6">
                <div className="text-center">
                    <div className="text-4xl mb-3">🖱️</div>
                    <p className="text-gray-400 text-sm">选择一个节点以编辑属性</p>
                </div>
            </div>
        );
    }

    const { id, type, data } = selectedNode;

    const handleChange = (key: string, value: any) => {
        updateNodeData(id, { [key]: value });
    };

    return (
        <div className="w-80 bg-gray-900/80 backdrop-blur-xl border-l border-gray-700/50 flex flex-col overflow-y-auto">
            {/* Header */}
            <div className="p-4 border-b border-gray-700/50">
                <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider">属性设置</h3>
                <p className="text-xs text-gray-500 mt-1">Node ID: {id}</p>
            </div>

            <div className="p-4 space-y-4">
                {/* Common: Label */}
                <div>
                    <label className="block text-xs font-medium text-gray-400 mb-1.5">标签名称</label>
                    <input
                        type="text"
                        value={(data.label as string) || ''}
                        onChange={(e) => handleChange('label', e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200
              focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    />
                </div>

                {/* Python Node: Code Editor */}
                {type === 'python' && (
                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1.5">Python 代码</label>
                        <div className="border border-gray-700 rounded-lg overflow-hidden" style={{ height: 300 }}>
                            <MonacoEditor
                                height="100%"
                                language="python"
                                theme="vs-dark"
                                value={(data.code as string) || '# Write your Python code here\n# Use "inputs" to access upstream data\n# Set "output" to pass data downstream\n\noutput = "Hello from KKRPA!"'}
                                onChange={(value) => handleChange('code', value || '')}
                                options={{
                                    minimap: { enabled: false },
                                    fontSize: 13,
                                    scrollBeyondLastLine: false,
                                    wordWrap: 'on',
                                    lineNumbers: 'on',
                                    tabSize: 4,
                                    automaticLayout: true,
                                }}
                            />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                            使用 <code className="text-blue-400">inputs</code> 访问上游数据，设置{' '}
                            <code className="text-blue-400">output</code> 向下传递
                        </p>
                    </div>
                )}

                {/* HTTP Node */}
                {type === 'http' && (
                    <>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">请求方法</label>
                            <select
                                value={(data.method as string) || 'GET'}
                                onChange={(e) => handleChange('method', e.target.value)}
                                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 outline-none"
                            >
                                {['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map((m) => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">URL</label>
                            <input
                                type="text"
                                value={(data.url as string) || ''}
                                onChange={(e) => handleChange('url', e.target.value)}
                                placeholder="https://api.example.com/data"
                                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200
                  focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">请求体 (JSON)</label>
                            <textarea
                                value={(data.body as string) || ''}
                                onChange={(e) => handleChange('body', e.target.value)}
                                rows={4}
                                placeholder='{"key": "value"}'
                                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200
                  font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                            />
                        </div>
                    </>
                )}

                {/* Condition Node */}
                {type === 'condition' && (
                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1.5">条件表达式</label>
                        <input
                            type="text"
                            value={(data.condition as string) || ''}
                            onChange={(e) => handleChange('condition', e.target.value)}
                            placeholder='inputs["_latest"]["status_code"] == 200'
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200
                font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            True → 绿色分支 | False → 红色分支
                        </p>
                    </div>
                )}

                {/* Loop Node */}
                {type === 'loop' && (
                    <>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5">循环类型</label>
                            <select
                                value={(data.loop_type as string) || 'count'}
                                onChange={(e) => handleChange('loop_type', e.target.value)}
                                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 outline-none"
                            >
                                <option value="count">计数循环</option>
                                <option value="for_each">遍历列表</option>
                            </select>
                        </div>
                        {(data.loop_type || 'count') === 'count' && (
                            <div>
                                <label className="block text-xs font-medium text-gray-400 mb-1.5">次数</label>
                                <input
                                    type="number"
                                    min={1}
                                    max={100}
                                    value={(data.count as number) || 1}
                                    onChange={(e) => handleChange('count', parseInt(e.target.value) || 1)}
                                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 outline-none"
                                />
                            </div>
                        )}
                    </>
                )}

                {/* Delay Node */}
                {type === 'delay' && (
                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1.5">等待时间 (秒)</label>
                        <input
                            type="number"
                            min={0}
                            max={300}
                            value={(data.seconds as number) || 1}
                            onChange={(e) => handleChange('seconds', parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 outline-none"
                        />
                    </div>
                )}
            </div>
        </div>
    );
}
