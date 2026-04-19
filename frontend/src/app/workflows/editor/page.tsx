'use client';

import { Suspense, useState, useCallback, useEffect } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useWorkflowStore } from '@/lib/store';
import { workflowAPI } from '@/lib/api';
import Canvas from '@/components/workflow/Canvas';
import NodePalette from '@/components/workflow/NodePalette';
import PropertyPanel from '@/components/workflow/PropertyPanel';
import Toolbar from '@/components/workflow/Toolbar';

function WorkflowEditorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = searchParams.get('id') || '';
  const {
    nodes, edges, workflowName, isDirty,
    setNodes, setEdges, setWorkflowMeta, setDirty, reset,
  } = useWorkflowStore();

  const [saving, setSaving] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [workflowId, setWorkflowId] = useState<number | null>(null);

  // Load workflow
  useEffect(() => {
    const numId = parseInt(id);
    if (isNaN(numId)) return;
    setWorkflowId(numId);

    const load = async () => {
      try {
        const res = await workflowAPI.get(numId);
        const wf = res.data;
        setWorkflowMeta(wf.id, wf.name);
        setNodes(wf.graph_data?.nodes || []);
        setEdges(wf.graph_data?.edges || []);
        setDirty(false);
      } catch (err) {
        console.error('Failed to load workflow', err);
      }
    };
    load();
    return () => reset();
  }, [id]);

  const handleSave = useCallback(async () => {
    if (!workflowId) return;
    setSaving(true);
    try {
      await workflowAPI.update(workflowId, {
        graph_data: { nodes, edges },
      });
      setDirty(false);
    } catch (err) {
      console.error('Save failed', err);
    }
    setSaving(false);
  }, [workflowId, nodes, edges, setDirty]);

  const handleExecute = useCallback(async () => {
    if (!workflowId) return;
    if (isDirty) await handleSave();
    setExecuting(true);
    try {
      const res = await workflowAPI.execute(workflowId);
      alert(`任务已提交！ID: ${res.data.id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Execution failed');
    }
    setExecuting(false);
  }, [workflowId, isDirty, handleSave]);

  const onDragStart = useCallback((event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  }, []);

  return (
    <ReactFlowProvider>
      <div className="h-screen flex flex-col bg-gray-950">
        <Toolbar
          workflowName={workflowName}
          isDirty={isDirty}
          onSave={handleSave}
          onExecute={handleExecute}
          onBack={() => router.push('/workflows')}
          saving={saving}
          executing={executing}
        />
        <div className="flex flex-1 overflow-hidden">
          <NodePalette onDragStart={onDragStart} />
          <Canvas />
          <PropertyPanel />
        </div>
      </div>
    </ReactFlowProvider>
  );
}

export default function WorkflowEditorPage() {
  return (
    <Suspense fallback={
      <div className="h-screen flex items-center justify-center bg-gray-950">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <WorkflowEditorContent />
    </Suspense>
  );
}
