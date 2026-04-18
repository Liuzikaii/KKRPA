'use client';

import { useCallback, useRef, useMemo } from 'react';
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    addEdge,
    Connection,
    ReactFlowProvider,
    ReactFlowInstance,
    BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useWorkflowStore } from '@/lib/store';
import { customNodeTypes } from './CustomNodes';

let nodeIdCounter = 0;
const getNodeId = () => `node_${Date.now()}_${++nodeIdCounter}`;

export default function Canvas() {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const reactFlowInstance = useRef<ReactFlowInstance | null>(null);

    const {
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        setEdges,
        addNode,
        setSelectedNode,
    } = useWorkflowStore();

    const onConnect = useCallback(
        (params: Connection) => {
            setEdges(addEdge({ ...params, animated: true, style: { stroke: '#4b5563', strokeWidth: 2 } }, edges));
        },
        [edges, setEdges]
    );

    const onNodeClick = useCallback(
        (_event: React.MouseEvent, node: any) => {
            setSelectedNode(node);
        },
        [setSelectedNode]
    );

    const onPaneClick = useCallback(() => {
        setSelectedNode(null);
    }, [setSelectedNode]);

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();
            const nodeType = event.dataTransfer.getData('application/reactflow');
            if (!nodeType || !reactFlowInstance.current) return;

            const position = reactFlowInstance.current.screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            });

            const defaultLabels: Record<string, string> = {
                start: '开始',
                end: '结束',
                python: 'Python',
                http: 'HTTP 请求',
                condition: '条件判断',
                loop: '循环',
                delay: '延时',
            };

            const newNode = {
                id: getNodeId(),
                type: nodeType,
                position,
                data: {
                    label: defaultLabels[nodeType] || nodeType,
                },
            };

            addNode(newNode);
        },
        [addNode]
    );

    const onInit = useCallback((instance: ReactFlowInstance) => {
        reactFlowInstance.current = instance;
    }, []);

    const onDragStart = useCallback((event: React.DragEvent, nodeType: string) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.effectAllowed = 'move';
    }, []);

    // Memoize node types to prevent re-rendering
    const nodeTypes = useMemo(() => customNodeTypes, []);

    return (
        <div ref={reactFlowWrapper} className="flex-1 h-full">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onInit={onInit}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onNodeClick={onNodeClick}
                onPaneClick={onPaneClick}
                nodeTypes={nodeTypes}
                fitView
                proOptions={{ hideAttribution: true }}
                defaultEdgeOptions={{
                    animated: true,
                    style: { stroke: '#4b5563', strokeWidth: 2 },
                }}
                className="bg-gray-950"
            >
                <Background
                    variant={BackgroundVariant.Dots}
                    gap={20}
                    size={1}
                    color="#1f2937"
                />
                <Controls
                    className="!bg-gray-800 !border-gray-700 !rounded-xl !shadow-xl [&>button]:!bg-gray-800 [&>button]:!border-gray-700 [&>button]:!text-gray-300 [&>button:hover]:!bg-gray-700"
                />
                <MiniMap
                    className="!bg-gray-800 !border-gray-700 !rounded-xl"
                    nodeColor={(node) => {
                        const colors: Record<string, string> = {
                            start: '#10b981',
                            end: '#ef4444',
                            python: '#3b82f6',
                            http: '#8b5cf6',
                            condition: '#f59e0b',
                            loop: '#06b6d4',
                            delay: '#ec4899',
                        };
                        return colors[node.type || ''] || '#6b7280';
                    }}
                    maskColor="rgba(0, 0, 0, 0.6)"
                />
            </ReactFlow>
        </div>
    );
}

// Export the drag start handler as a named export
export { Canvas };
