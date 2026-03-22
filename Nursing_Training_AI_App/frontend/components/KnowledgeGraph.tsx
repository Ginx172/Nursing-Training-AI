import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
    ConnectionMode,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { Loader2 } from 'lucide-react';

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

const KnowledgeGraph = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);
            // In a real scenario, use the actual backend URL
            const response = await axios.get('http://localhost:8000/graph/data');

            const { nodes: backendNodes, edges: backendEdges } = response.data;

            // Transform backend nodes to ReactFlow nodes
            const rfNodes: Node[] = backendNodes.map((node: any, index: number) => ({
                id: node.id,
                data: { label: node.label },
                position: { x: Math.random() * 500, y: Math.random() * 500 }, // Random layout for now
                type: node.type === 'topic' ? 'input' : 'default',
                style: {
                    background: node.color,
                    color: '#fff',
                    width: node.type === 'topic' ? 100 : 150,
                    fontSize: 12,
                    borderRadius: 5,
                    padding: 10,
                },
            }));

            // Transform backend edges to ReactFlow edges
            const rfEdges: Edge[] = backendEdges.map((edge: any) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                animated: edge.animated,
                style: { stroke: '#999' },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                },
            }));

            setNodes(rfNodes);
            setEdges(rfEdges);
        } catch (err) {
            console.error("Failed to fetch graph data:", err);
            // Fallback data for demonstration if backend is not ready
            if (process.env.NODE_ENV === 'development') {
                setNodes([
                    { id: '1', position: { x: 0, y: 0 }, data: { label: 'Cardiology' }, style: { background: '#4a90e2', color: 'white' } },
                    { id: '2', position: { x: 0, y: 100 }, data: { label: 'ECG Basics' }, style: { background: '#e24a4a', color: 'white' } },
                ]);
                setEdges([{ id: 'e1-2', source: '1', target: '2' }]);
            } else {
                setError("Could not load knowledge graph.");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges],
    );

    if (loading) {
        return (
            <div className="flex h-[500px] w-full items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                <span className="ml-2 text-gray-500">Loading Knowledge Graph...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex h-[500px] w-full items-center justify-center bg-red-50 rounded-xl border border-red-200">
                <p className="text-red-500">{error}</p>
            </div>
        );
    }

    return (
        <div className="h-[600px] w-full rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
            <div className="border-b border-gray-100 bg-gray-50 px-4 py-3 flex justify-between items-center">
                <h3 className="font-semibold text-gray-800">Knowledge Graph Visualization</h3>
                <button
                    onClick={fetchData}
                    className="text-xs bg-white border border-gray-200 px-2 py-1 rounded hover:bg-gray-50"
                >
                    Refresh
                </button>
            </div>
            <div className="h-full w-full">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    connectionMode={ConnectionMode.Loose}
                    fitView
                >
                    <Background color="#f1f5f9" gap={16} />
                    <Controls />
                    <MiniMap />
                </ReactFlow>
            </div>
        </div>
    );
};

export default KnowledgeGraph;
