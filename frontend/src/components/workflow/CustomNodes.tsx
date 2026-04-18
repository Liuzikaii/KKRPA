'use client';

import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

/* ==================== Custom Node Styles ==================== */
const nodeColors: Record<string, string> = {
    start: '#10b981',
    end: '#ef4444',
    python: '#3b82f6',
    http: '#8b5cf6',
    condition: '#f59e0b',
    loop: '#06b6d4',
    delay: '#ec4899',
};

const nodeIcons: Record<string, string> = {
    start: '▶️',
    end: '⏹️',
    python: '🐍',
    http: '🌐',
    condition: '🔀',
    loop: '🔄',
    delay: '⏰',
};

/* ==================== Base Node Wrapper ==================== */
function BaseNodeComponent({
    data,
    type,
    selected,
    hasInput = true,
    hasOutput = true,
    extraHandles,
}: {
    data: any;
    type: string;
    selected: boolean;
    hasInput?: boolean;
    hasOutput?: boolean;
    extraHandles?: React.ReactNode;
}) {
    const color = nodeColors[type] || '#6b7280';
    const icon = nodeIcons[type] || '📦';

    return (
        <div
            className={`
        relative min-w-[180px] rounded-xl shadow-lg border-2 transition-all duration-200
        ${selected ? 'ring-2 ring-blue-400 ring-offset-2 ring-offset-gray-900 scale-105' : ''}
      `}
            style={{
                borderColor: color,
                background: 'rgba(17, 24, 39, 0.95)',
                backdropFilter: 'blur(10px)',
            }}
        >
            {/* Header */}
            <div
                className="flex items-center gap-2 px-3 py-2 rounded-t-[10px] text-white text-sm font-semibold"
                style={{ background: `linear-gradient(135deg, ${color}dd, ${color}88)` }}
            >
                <span className="text-base">{icon}</span>
                <span>{data.label || type}</span>
            </div>

            {/* Body */}
            {data.description && (
                <div className="px-3 py-2 text-xs text-gray-400 border-t border-gray-700/50">
                    {data.description}
                </div>
            )}

            {/* Status indicator */}
            {data.status && (
                <div className="px-3 py-1.5 flex items-center gap-1.5 text-xs">
                    <span
                        className={`w-2 h-2 rounded-full ${data.status === 'running'
                                ? 'bg-yellow-400 animate-pulse'
                                : data.status === 'success'
                                    ? 'bg-green-400'
                                    : data.status === 'error'
                                        ? 'bg-red-400'
                                        : 'bg-gray-500'
                            }`}
                    />
                    <span className="text-gray-400 capitalize">{data.status}</span>
                </div>
            )}

            {/* Handles */}
            {hasInput && (
                <Handle
                    type="target"
                    position={Position.Top}
                    className="!w-3 !h-3 !border-2 !border-gray-600 !bg-gray-800 hover:!bg-blue-400 transition-colors"
                />
            )}
            {hasOutput && (
                <Handle
                    type="source"
                    position={Position.Bottom}
                    className="!w-3 !h-3 !border-2 !border-gray-600 !bg-gray-800 hover:!bg-blue-400 transition-colors"
                />
            )}
            {extraHandles}
        </div>
    );
}

/* ==================== Individual Node Types ==================== */

export const StartNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{ ...data, label: data.label || '开始' }}
        type="start"
        selected={!!selected}
        hasInput={false}
        hasOutput={true}
    />
));
StartNode.displayName = 'StartNode';

export const EndNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{ ...data, label: data.label || '结束' }}
        type="end"
        selected={!!selected}
        hasInput={true}
        hasOutput={false}
    />
));
EndNode.displayName = 'EndNode';

export const PythonNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{
            ...data,
            label: data.label || 'Python',
            description: data.code
                ? `${(data.code as string).split('\n').length} lines`
                : 'Click to edit code',
        }}
        type="python"
        selected={!!selected}
    />
));
PythonNode.displayName = 'PythonNode';

export const HttpNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{
            ...data,
            label: data.label || 'HTTP 请求',
            description: data.url ? `${data.method || 'GET'} ${data.url}` : 'Configure request',
        }}
        type="http"
        selected={!!selected}
    />
));
HttpNode.displayName = 'HttpNode';

export const ConditionNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{
            ...data,
            label: data.label || '条件判断',
            description: data.condition || 'Set condition',
        }}
        type="condition"
        selected={!!selected}
        extraHandles={
            <>
                <Handle
                    type="source"
                    position={Position.Bottom}
                    id="true"
                    className="!w-3 !h-3 !border-2 !border-green-500 !bg-green-600 hover:!bg-green-400 transition-colors"
                    style={{ left: '30%' }}
                />
                <Handle
                    type="source"
                    position={Position.Bottom}
                    id="false"
                    className="!w-3 !h-3 !border-2 !border-red-500 !bg-red-600 hover:!bg-red-400 transition-colors"
                    style={{ left: '70%' }}
                />
            </>
        }
        hasOutput={false}
    />
));
ConditionNode.displayName = 'ConditionNode';

export const LoopNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{
            ...data,
            label: data.label || '循环',
            description: data.loop_type === 'for_each' ? 'For each item' : `${data.count || 1} times`,
        }}
        type="loop"
        selected={!!selected}
    />
));
LoopNode.displayName = 'LoopNode';

export const DelayNode = memo(({ data, selected }: NodeProps) => (
    <BaseNodeComponent
        data={{
            ...data,
            label: data.label || '延时',
            description: `Wait ${data.seconds || 1}s`,
        }}
        type="delay"
        selected={!!selected}
    />
));
DelayNode.displayName = 'DelayNode';

// Export node type mapping for React Flow
export const customNodeTypes = {
    start: StartNode,
    end: EndNode,
    python: PythonNode,
    http: HttpNode,
    condition: ConditionNode,
    loop: LoopNode,
    delay: DelayNode,
};
