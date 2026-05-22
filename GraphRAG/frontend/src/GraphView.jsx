import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";


/* ------------------------------------------------------------------ */
/* Entity Type Colors                                                 */
/* ------------------------------------------------------------------ */

const TYPE_COLORS = {
  Person: "#4ade80",       // Green
  Organization: "#60a5fa", // Blue
  Product: "#f97316",      // Orange
  Concept: "#c084fc",      // Purple
  Place: "#fbbf24",        // Yellow
  Event: "#f87171",        // Red
  Unknown: "#94a3b8",      // Gray
};


/* ------------------------------------------------------------------ */
/* Graph View Component                                               */
/* ------------------------------------------------------------------ */

export default function GraphView({
  highlightNodes = [],
}) {

  /* ---------------------------------------------------------------- */
  /* State                                                            */
  /* ---------------------------------------------------------------- */

  const [graphData, setGraphData] = useState({
    nodes: [],
    links: [],
  });

  const [selectedNode, setSelectedNode] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const containerRef = useRef(null);

  const [dimensions, setDimensions] = useState({
    width: 800,
    height: 600,
  });


  /* ---------------------------------------------------------------- */
  /* Fetch Graph on Mount                                             */
  /* ---------------------------------------------------------------- */

  useEffect(() => {
    fetchGraph();
  }, []);


  /* ---------------------------------------------------------------- */
  /* Responsive Resize Handling                                       */
  /* ---------------------------------------------------------------- */

  useEffect(() => {

    if (!containerRef.current) return;

    const observer = new ResizeObserver((entries) => {

      for (const entry of entries) {

        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
    };

  }, []);


  /* ---------------------------------------------------------------- */
  /* Fetch Full Graph                                                 */
  /* ---------------------------------------------------------------- */

  async function fetchGraph() {

    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/graph");

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const data = await response.json();

      setGraphData(data);

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);
    }
  }


  /* ---------------------------------------------------------------- */
  /* Highlighted Nodes                                                */
  /* ---------------------------------------------------------------- */

  const highlightSet = new Set(
    highlightNodes.map((node) => node.name)
  );


  /* ---------------------------------------------------------------- */
  /* Loading State                                                    */
  /* ---------------------------------------------------------------- */

  if (loading) {

    return (
      <div style={styles.loadingContainer}>
        <p style={styles.loadingText}>
          Loading knowledge graph...
        </p>
      </div>
    );
  }


  /* ---------------------------------------------------------------- */
  /* Error State                                                      */
  /* ---------------------------------------------------------------- */

  if (error) {

    return (
      <div style={styles.errorContainer}>

        <p style={styles.errorText}>
          Error: {error}
        </p>

        <button
          onClick={fetchGraph}
          style={styles.retryButton}
        >
          Retry
        </button>

      </div>
    );
  }


  /* ---------------------------------------------------------------- */
  /* Main Render                                                      */
  /* ---------------------------------------------------------------- */

  return (
    <div style={styles.wrapper}>

      {/* ------------------------------------------------------------ */}
      {/* Stats Bar                                                    */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.statsBar}>

        <span>
          {graphData.nodes.length} nodes
        </span>

        <span style={{ margin: "0 12px" }}>
          ·
        </span>

        <span>
          {graphData.links.length} relationships
        </span>

        <button
          onClick={fetchGraph}
          style={styles.refreshButton}
        >
          ↻ Refresh
        </button>

      </div>


      {/* ------------------------------------------------------------ */}
      {/* Graph Container                                              */}
      {/* ------------------------------------------------------------ */}

      <div
        ref={containerRef}
        style={styles.graphContainer}
      >

        <ForceGraph2D
          graphData={graphData}
          width={dimensions.width}
          height={dimensions.height}


          /* -------------------------------------------------------- */
          /* Node Appearance                                          */
          /* -------------------------------------------------------- */

          nodeLabel="name"

          nodeColor={(node) => {

            // Highlight queried nodes
            if (highlightSet.has(node.id)) {
              return "#ffffff";
            }

            return (
              TYPE_COLORS[node.type] ||
              TYPE_COLORS.Unknown
            );
          }}

          nodeRelSize={6}


          /* -------------------------------------------------------- */
          /* Custom Node Rendering                                    */
          /* -------------------------------------------------------- */

          nodeCanvasObject={(
            node,
            ctx,
            globalScale
          ) => {

            const label = node.name;

            const radius = 6;

            const fontSize = 12 / globalScale;


            // Draw circle
            ctx.beginPath();

            ctx.arc(
              node.x,
              node.y,
              radius,
              0,
              2 * Math.PI
            );

            ctx.fillStyle = highlightSet.has(node.id)
              ? "#ffffff"
              : (
                  TYPE_COLORS[node.type] ||
                  TYPE_COLORS.Unknown
                );

            ctx.fill();


            // Show labels only when zoomed in
            if (globalScale > 1.5) {

              ctx.font = `${fontSize}px Sans-Serif`;

              ctx.textAlign = "center";

              ctx.textBaseline = "top";

              ctx.fillStyle = "#e2e8f0";

              ctx.fillText(
                label,
                node.x,
                node.y + radius + 2
              );
            }
          }}


          /* -------------------------------------------------------- */
          /* Link Appearance                                          */
          /* -------------------------------------------------------- */

          linkLabel="relation"

          linkColor={() => "#475569"}

          linkWidth={1.5}

          linkDirectionalArrowLength={4}

          linkDirectionalArrowRelPos={1}


          /* -------------------------------------------------------- */
          /* Link Labels                                               */
          /* -------------------------------------------------------- */

          linkCanvasObjectMode={() => "after"}

          linkCanvasObject={(
            link,
            ctx,
            globalScale
          ) => {

            // Show only when zoomed in
            if (globalScale < 2) return;

            const start = link.source;
            const end = link.target;

            // Midpoint of the line
            const textPos = {
              x: start.x + (end.x - start.x) / 2,
              y: start.y + (end.y - start.y) / 2,
            };

            const label = link.relation || "";

            const fontSize = 8 / globalScale;

            ctx.font = `${fontSize}px Sans-Serif`;

            ctx.textAlign = "center";

            ctx.textBaseline = "middle";

            ctx.fillStyle = "#94a3b8";

            ctx.fillText(
              label,
              textPos.x,
              textPos.y
            );
          }}


          /* -------------------------------------------------------- */
          /* Node Click                                                */
          /* -------------------------------------------------------- */

          onNodeClick={(node) => {
            setSelectedNode(node);
          }}


          /* -------------------------------------------------------- */
          /* Physics                                                   */
          /* -------------------------------------------------------- */

          d3AlphaDecay={0.02}

          d3VelocityDecay={0.3}

          cooldownTicks={100}

          backgroundColor="#0f172a"
        />

      </div>


      {/* ------------------------------------------------------------ */}
      {/* Node Details Panel                                           */}
      {/* ------------------------------------------------------------ */}

      {selectedNode && (

        <div style={styles.nodePanel}>

          <button
            onClick={() => setSelectedNode(null)}
            style={styles.closeButton}
          >
            ✕
          </button>

          <h3
            style={{
              color: "#f1f5f9",
              margin: "0 0 8px",
            }}
          >
            {selectedNode.name}
          </h3>

          <p
            style={{
              color: "#94a3b8",
              margin: 0,
            }}
          >
            Type: {selectedNode.type}
          </p>

        </div>
      )}


      {/* ------------------------------------------------------------ */}
      {/* Legend                                                       */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.legend}>

        {Object.entries(TYPE_COLORS).map(
          ([type, color]) => (

            <div
              key={type}
              style={styles.legendItem}
            >

              <div
                style={{
                  ...styles.legendDot,
                  backgroundColor: color,
                }}
              />

              <span
                style={{
                  color: "#94a3b8",
                  fontSize: 11,
                }}
              >
                {type}
              </span>

            </div>
          )
        )}

      </div>

    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Styles                                                             */
/* ------------------------------------------------------------------ */

const styles = {

  wrapper: {
    position: "relative",
    width: "100%",
    height: "100%",
    background: "#0f172a",
    borderRadius: "8px",
    overflow: "hidden",
  },

  statsBar: {
    position: "absolute",
    top: 12,
    left: 12,
    zIndex: 10,
    background: "rgba(15,23,42,0.8)",
    color: "#94a3b8",
    padding: "6px 12px",
    borderRadius: "6px",
    fontSize: 13,
    display: "flex",
    alignItems: "center",
  },

  graphContainer: {
    width: "100%",
    height: "100%",
  },

  loadingContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    background: "#0f172a",
  },

  loadingText: {
    color: "#94a3b8",
    fontSize: 16,
  },

  errorContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    background: "#0f172a",
    gap: 12,
  },

  errorText: {
    color: "#f87171",
    fontSize: 14,
  },

  retryButton: {
    background: "#3b82f6",
    color: "white",
    border: "none",
    padding: "8px 16px",
    borderRadius: "6px",
    cursor: "pointer",
  },

  refreshButton: {
    marginLeft: 12,
    background: "none",
    border: "1px solid #334155",
    color: "#94a3b8",
    padding: "2px 8px",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: 13,
  },

  nodePanel: {
    position: "absolute",
    top: 12,
    right: 12,
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "8px",
    padding: 16,
    minWidth: 200,
    zIndex: 20,
  },

  closeButton: {
    position: "absolute",
    top: 8,
    right: 8,
    background: "none",
    border: "none",
    color: "#94a3b8",
    cursor: "pointer",
    fontSize: 16,
  },

  legend: {
    position: "absolute",
    bottom: 12,
    left: 12,
    display: "flex",
    flexWrap: "wrap",
    gap: "6px 12px",
    maxWidth: 400,
  },

  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: 4,
  },

  legendDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
  },
};