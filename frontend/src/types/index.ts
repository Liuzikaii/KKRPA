export interface WorkflowNode {
    id: string;
    type: string;
    position: { x: number; y: number };
    data: Record<string, any>;
}

export interface WorkflowEdge {
    id: string;
    source: string;
    target: string;
    sourceHandle?: string;
    targetHandle?: string;
}

export interface Workflow {
    id: number;
    name: string;
    description: string;
    owner_id: number;
    graph_data: {
        nodes: WorkflowNode[];
        edges: WorkflowEdge[];
    };
    version: number;
    is_active: boolean;
    edition_required: string;
    created_at: string;
    updated_at: string;
}

export interface TaskExecution {
    id: number;
    workflow_id: number;
    triggered_by: number | null;
    trigger_type: string;
    status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled';
    started_at: string | null;
    finished_at: string | null;
    result: Record<string, any>;
    logs: string;
    error: string;
    created_at: string;
}

export interface Schedule {
    id: number;
    workflow_id: number;
    created_by: number;
    cron_expression: string;
    timezone: string;
    is_enabled: boolean;
    next_run_at: string | null;
    last_run_at: string | null;
    created_at: string;
    updated_at: string;
}

export interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    edition: string;
    is_active: boolean;
    created_at: string;
}

// Node types for the palette
export const NODE_TYPES = [
    {
        type: 'start',
        label: '开始',
        description: '工作流起点',
        icon: '▶️',
        color: '#10b981',
        category: 'control',
    },
    {
        type: 'end',
        label: '结束',
        description: '工作流终点',
        icon: '⏹️',
        color: '#ef4444',
        category: 'control',
    },
    {
        type: 'python',
        label: 'Python',
        description: '执行 Python 代码',
        icon: '🐍',
        color: '#3b82f6',
        category: 'action',
    },
    {
        type: 'http',
        label: 'HTTP 请求',
        description: '发送 HTTP/API 请求',
        icon: '🌐',
        color: '#8b5cf6',
        category: 'action',
    },
    {
        type: 'condition',
        label: '条件判断',
        description: 'If/Else 条件分支',
        icon: '🔀',
        color: '#f59e0b',
        category: 'logic',
    },
    {
        type: 'loop',
        label: '循环',
        description: '重复执行',
        icon: '🔄',
        color: '#06b6d4',
        category: 'logic',
    },
    {
        type: 'delay',
        label: '延时',
        description: '等待指定时间',
        icon: '⏰',
        color: '#ec4899',
        category: 'logic',
    },
] as const;
