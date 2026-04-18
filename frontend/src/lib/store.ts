import { create } from 'zustand';
import { Node, Edge } from '@xyflow/react';

// ==================== Auth Store ====================
interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    edition: string;
    is_active: boolean;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    setAuth: (user: User, token: string) => void;
    logout: () => void;
    loadFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: null,
    isAuthenticated: false,
    setAuth: (user, token) => {
        localStorage.setItem('kkrpa_token', token);
        localStorage.setItem('kkrpa_user', JSON.stringify(user));
        set({ user, token, isAuthenticated: true });
    },
    logout: () => {
        localStorage.removeItem('kkrpa_token');
        localStorage.removeItem('kkrpa_user');
        set({ user: null, token: null, isAuthenticated: false });
    },
    loadFromStorage: () => {
        if (typeof window === 'undefined') return;
        const token = localStorage.getItem('kkrpa_token');
        const userStr = localStorage.getItem('kkrpa_user');
        if (token && userStr) {
            try {
                const user = JSON.parse(userStr);
                set({ user, token, isAuthenticated: true });
            } catch {
                set({ user: null, token: null, isAuthenticated: false });
            }
        }
    },
}));

// ==================== Workflow Editor Store ====================
interface WorkflowEditorState {
    nodes: Node[];
    edges: Edge[];
    selectedNode: Node | null;
    workflowId: number | null;
    workflowName: string;
    isDirty: boolean;
    setNodes: (nodes: Node[]) => void;
    setEdges: (edges: Edge[]) => void;
    onNodesChange: (changes: any) => void;
    onEdgesChange: (changes: any) => void;
    setSelectedNode: (node: Node | null) => void;
    setWorkflowMeta: (id: number, name: string) => void;
    setDirty: (dirty: boolean) => void;
    addNode: (node: Node) => void;
    updateNodeData: (nodeId: string, data: any) => void;
    reset: () => void;
}

export const useWorkflowStore = create<WorkflowEditorState>((set, get) => ({
    nodes: [],
    edges: [],
    selectedNode: null,
    workflowId: null,
    workflowName: 'Untitled Workflow',
    isDirty: false,
    setNodes: (nodes) => set({ nodes, isDirty: true }),
    setEdges: (edges) => set({ edges, isDirty: true }),
    onNodesChange: (changes: any) => {
        const { applyNodeChanges } = require('@xyflow/react');
        set((state) => ({
            nodes: applyNodeChanges(changes, state.nodes),
            isDirty: true,
        }));
    },
    onEdgesChange: (changes: any) => {
        const { applyEdgeChanges } = require('@xyflow/react');
        set((state) => ({
            edges: applyEdgeChanges(changes, state.edges),
            isDirty: true,
        }));
    },
    setSelectedNode: (node) => set({ selectedNode: node }),
    setWorkflowMeta: (id, name) => set({ workflowId: id, workflowName: name }),
    setDirty: (dirty) => set({ isDirty: dirty }),
    addNode: (node) =>
        set((state) => ({ nodes: [...state.nodes, node], isDirty: true })),
    updateNodeData: (nodeId, data) =>
        set((state) => ({
            nodes: state.nodes.map((n) =>
                n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
            ),
            isDirty: true,
        })),
    reset: () =>
        set({
            nodes: [],
            edges: [],
            selectedNode: null,
            workflowId: null,
            workflowName: 'Untitled Workflow',
            isDirty: false,
        }),
}));
