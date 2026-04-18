'use client';

interface ToolbarProps {
    workflowName: string;
    isDirty: boolean;
    onSave: () => void;
    onExecute: () => void;
    onBack: () => void;
    saving?: boolean;
    executing?: boolean;
}

export default function Toolbar({
    workflowName,
    isDirty,
    onSave,
    onExecute,
    onBack,
    saving = false,
    executing = false,
}: ToolbarProps) {
    return (
        <div className="h-14 bg-gray-900/90 backdrop-blur-xl border-b border-gray-700/50 flex items-center justify-between px-4">
            {/* Left */}
            <div className="flex items-center gap-3">
                <button
                    onClick={onBack}
                    className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1.5"
                >
                    ← 返回
                </button>
                <div className="w-px h-6 bg-gray-700" />
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                    {workflowName}
                    {isDirty && <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" title="未保存" />}
                </h2>
            </div>

            {/* Right */}
            <div className="flex items-center gap-2">
                <button
                    onClick={onSave}
                    disabled={saving || !isDirty}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
            ${isDirty
                            ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/25'
                            : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                        } ${saving ? 'opacity-60' : ''}`}
                >
                    {saving ? '保存中...' : '💾 保存'}
                </button>
                <button
                    onClick={onExecute}
                    disabled={executing}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
            bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/25
            ${executing ? 'opacity-60' : ''}`}
                >
                    {executing ? '执行中...' : '▶ 执行'}
                </button>
            </div>
        </div>
    );
}
