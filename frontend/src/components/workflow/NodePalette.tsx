'use client';

import { NODE_TYPES } from '@/types';

interface NodePaletteProps {
    onDragStart: (event: React.DragEvent, nodeType: string) => void;
}

export default function NodePalette({ onDragStart }: NodePaletteProps) {
    const categories = {
        control: { label: '控制', items: NODE_TYPES.filter((n) => n.category === 'control') },
        action: { label: '动作', items: NODE_TYPES.filter((n) => n.category === 'action') },
        logic: { label: '逻辑', items: NODE_TYPES.filter((n) => n.category === 'logic') },
    };

    return (
        <div className="w-56 bg-gray-900/80 backdrop-blur-xl border-r border-gray-700/50 flex flex-col overflow-y-auto">
            <div className="p-4 border-b border-gray-700/50">
                <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider">节点面板</h3>
                <p className="text-xs text-gray-500 mt-1">拖拽节点到画布</p>
            </div>

            {Object.entries(categories).map(([key, cat]) => (
                <div key={key} className="p-3">
                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                        {cat.label}
                    </h4>
                    <div className="space-y-1.5">
                        {cat.items.map((nodeType) => (
                            <div
                                key={nodeType.type}
                                draggable
                                onDragStart={(e) => onDragStart(e, nodeType.type)}
                                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-grab active:cursor-grabbing
                  bg-gray-800/60 hover:bg-gray-700/80 border border-gray-700/30 hover:border-gray-600
                  transition-all duration-150 group"
                                style={{
                                    borderLeftColor: nodeType.color,
                                    borderLeftWidth: '3px',
                                }}
                            >
                                <span className="text-lg group-hover:scale-110 transition-transform">{nodeType.icon}</span>
                                <div>
                                    <div className="text-sm font-medium text-gray-200">{nodeType.label}</div>
                                    <div className="text-xs text-gray-500">{nodeType.description}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
