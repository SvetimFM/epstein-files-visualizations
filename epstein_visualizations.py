#!/usr/bin/env python3
"""
Epstein Files Data Visualizations for r/dataisbeautiful
Generates interactive HTML visualizations from embedding data.
"""

import json
import re
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime

# Configuration
EMBEDDINGS_FILE = "/tmp/epstein-full-embeddings/all_embeddings.json"
OUTPUT_DIR = "/mnt/j/DevWorkspace/Active Projects/Q_TicketTriage"

# Key names to search for in documents
KEY_NAMES = [
    "Epstein", "Maxwell", "Ghislaine", "Clinton", "Gates", "Trump", "Prince Andrew",
    "Dershowitz", "Chomsky", "Barak", "Nowak", "Krauss", "Church", "Pinker", "Minsky",
    "Brunel", "Wexner", "Dubin", "Mitchell", "Ovitz", "Visoski", "Kellen", "Marcinkova",
    "Roberts", "Virginia", "Nobel", "Harvard", "MIT", "ASU", "JEGE", "MC2",
    "Zorro", "Palm Beach", "Little St James", "New York"
]

def load_embeddings():
    """Load embeddings from JSON file."""
    print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
    with open(EMBEDDINGS_FILE, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} embeddings")
    return data

def extract_doc_info(filename):
    """Extract volume and type info from filename."""
    # Pattern: IMAGES-XXX-HOUSE_OVERSIGHT_XXXXXX.txt or TEXT-XXX-HOUSE_OVERSIGHT_XXXXXX.txt
    if filename.startswith("IMAGES"):
        doc_type = "IMAGES"
    elif filename.startswith("TEXT"):
        doc_type = "TEXT"
    else:
        doc_type = "OTHER"

    # Extract volume number
    match = re.search(r'-(\d{3})-', filename)
    volume = match.group(1) if match else "000"

    # Extract document number
    match = re.search(r'HOUSE_OVERSIGHT_(\d+)', filename)
    doc_num = int(match.group(1)) if match else 0

    return doc_type, volume, doc_num

def create_umap_visualization(embeddings_data, sample_size=10000):
    """Create UMAP dimensionality reduction visualization."""
    print("\n=== Creating UMAP Visualization ===")

    # Import UMAP here to avoid slow import if not needed
    import umap

    # Sample if too large
    if len(embeddings_data) > sample_size:
        print(f"Sampling {sample_size} from {len(embeddings_data)} embeddings...")
        indices = np.random.choice(len(embeddings_data), sample_size, replace=False)
        sampled_data = [embeddings_data[i] for i in indices]
    else:
        sampled_data = embeddings_data
        sample_size = len(embeddings_data)

    # Extract embeddings matrix
    print("Extracting embedding vectors...")
    embeddings = np.array([item['embedding'] for item in sampled_data])

    # Extract metadata
    filenames = [item.get('filename', '') for item in sampled_data]
    texts = [item.get('text_preview', '')[:100] for item in sampled_data]

    # Get document info
    doc_types = []
    volumes = []
    doc_nums = []
    for fn in filenames:
        dt, vol, num = extract_doc_info(fn)
        doc_types.append(dt)
        volumes.append(vol)
        doc_nums.append(num)

    # Run UMAP
    print(f"Running UMAP on {sample_size} embeddings (this may take a few minutes)...")
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        n_components=2,
        metric='cosine',
        random_state=42
    )
    embedding_2d = reducer.fit_transform(embeddings)
    print("UMAP complete!")

    # Create DataFrame
    df = pd.DataFrame({
        'x': embedding_2d[:, 0],
        'y': embedding_2d[:, 1],
        'doc_type': doc_types,
        'volume': volumes,
        'doc_num': doc_nums,
        'filename': filenames,
        'text_preview': texts
    })

    # Create interactive plot
    fig = px.scatter(
        df, x='x', y='y',
        color='doc_type',
        hover_data=['filename', 'volume', 'text_preview'],
        title=f'Epstein Files Embedding Space ({sample_size:,} documents)',
        labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
        color_discrete_map={'IMAGES': '#FF6B6B', 'TEXT': '#4ECDC4', 'OTHER': '#95A5A6'}
    )

    fig.update_layout(
        width=1200,
        height=800,
        template='plotly_white',
        font=dict(size=12),
        title_font_size=20
    )

    fig.update_traces(marker=dict(size=3, opacity=0.6))

    # Save
    output_path = f"{OUTPUT_DIR}/epstein_embedding_clusters.html"
    fig.write_html(output_path)
    print(f"Saved UMAP visualization to: {output_path}")

    return df

def extract_names_from_text(text):
    """Extract known names from text."""
    found = []
    text_upper = text.upper()
    for name in KEY_NAMES:
        if name.upper() in text_upper:
            found.append(name)
    return found

def create_network_graph(embeddings_data):
    """Create network graph of co-occurring names."""
    print("\n=== Creating Network Graph ===")

    # Count name occurrences and co-occurrences
    name_counts = Counter()
    co_occurrences = defaultdict(int)

    print("Extracting names from documents...")
    for i, item in enumerate(embeddings_data):
        text = item.get('text_preview', '')
        names = extract_names_from_text(text)

        # Count individual names
        for name in names:
            name_counts[name] += 1

        # Count co-occurrences
        for j, name1 in enumerate(names):
            for name2 in names[j+1:]:
                pair = tuple(sorted([name1, name2]))
                co_occurrences[pair] += 1

        if (i + 1) % 10000 == 0:
            print(f"  Processed {i+1:,} documents...")

    print(f"Found {len(name_counts)} unique names")

    # Build graph
    G = nx.Graph()

    # Add nodes
    for name, count in name_counts.items():
        if count >= 10:  # Only include names mentioned 10+ times
            G.add_node(name, count=count)

    # Add edges
    for (name1, name2), count in co_occurrences.items():
        if count >= 5 and name1 in G.nodes() and name2 in G.nodes():
            G.add_edge(name1, name2, weight=count)

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        count = G.nodes[node]['count']
        node_text.append(f"{node}<br>Mentions: {count}")
        node_size.append(min(count / 50, 50) + 10)  # Scale size

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[n for n in G.nodes()],
        textposition="top center",
        textfont=dict(size=8),
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlOrRd',
            size=node_size,
            color=[G.nodes[n]['count'] for n in G.nodes()],
            colorbar=dict(
                thickness=15,
                title='Mentions',
                xanchor='left'
            ),
            line_width=1
        )
    )

    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(text='Epstein Files: Network of Names and Connections', font=dict(size=20)),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       width=1200,
                       height=800,
                       template='plotly_white'
                   ))

    # Save
    output_path = f"{OUTPUT_DIR}/epstein_network_graph.html"
    fig.write_html(output_path)
    print(f"Saved network graph to: {output_path}")

    # Return stats for summary
    return {
        'name_counts': dict(name_counts.most_common(30)),
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges()
    }

def create_document_distribution(embeddings_data):
    """Create visualization of document distribution by type and volume."""
    print("\n=== Creating Document Distribution ===")

    # Extract doc info
    doc_types = []
    volumes = []

    for item in embeddings_data:
        filename = item.get('filename', '')
        dt, vol, _ = extract_doc_info(filename)
        doc_types.append(dt)
        volumes.append(f"{dt}-{vol}")

    # Count by type
    type_counts = Counter(doc_types)
    volume_counts = Counter(volumes)

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Document Types', 'Distribution by Volume'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )

    # Pie chart for types
    fig.add_trace(
        go.Pie(
            labels=list(type_counts.keys()),
            values=list(type_counts.values()),
            marker_colors=['#FF6B6B', '#4ECDC4', '#95A5A6']
        ),
        row=1, col=1
    )

    # Bar chart for volumes (top 20)
    top_volumes = volume_counts.most_common(20)
    fig.add_trace(
        go.Bar(
            x=[v[0] for v in top_volumes],
            y=[v[1] for v in top_volumes],
            marker_color='#667eea'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text=f'Epstein Files Document Distribution ({len(embeddings_data):,} chunks)',
        width=1200,
        height=500,
        template='plotly_white'
    )

    # Save
    output_path = f"{OUTPUT_DIR}/epstein_doc_distribution.html"
    fig.write_html(output_path)
    print(f"Saved document distribution to: {output_path}")

    return type_counts, volume_counts

def create_summary(embeddings_data, network_stats, type_counts):
    """Create markdown summary of visualizations."""
    print("\n=== Creating Summary ===")

    summary = f"""# Epstein Files Visualization Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Documents:** {len(embeddings_data):,} chunks

---

## Visualizations Created

### 1. Embedding Cluster Map
- **File:** `epstein_embedding_clusters.html`
- **Method:** UMAP dimensionality reduction (768-dim → 2D)
- **Purpose:** Shows semantic similarity between documents

### 2. Network Graph
- **File:** `epstein_network_graph.html`
- **Nodes:** {network_stats['num_nodes']} entities
- **Edges:** {network_stats['num_edges']} connections
- **Purpose:** Shows co-occurrence of names in documents

### 3. Document Distribution
- **File:** `epstein_doc_distribution.html`
- **Purpose:** Shows breakdown by document type and volume

---

## Key Statistics

### Document Types
| Type | Count | Percentage |
|------|-------|------------|
"""

    total = sum(type_counts.values())
    for dtype, count in type_counts.most_common():
        pct = count / total * 100
        summary += f"| {dtype} | {count:,} | {pct:.1f}% |\n"

    summary += f"""
### Top Mentioned Names
| Name | Mentions |
|------|----------|
"""

    for name, count in list(network_stats['name_counts'].items())[:20]:
        summary += f"| {name} | {count:,} |\n"

    summary += """
---

## How to Use

1. Open the HTML files in a web browser
2. Hover over points/nodes to see details
3. Zoom and pan to explore clusters
4. In the network graph, node size indicates mention frequency

---

*Generated from House Oversight Committee Epstein Document Release (November 2025)*
"""

    output_path = f"{OUTPUT_DIR}/EPSTEIN_VISUALIZATIONS_SUMMARY.md"
    with open(output_path, 'w') as f:
        f.write(summary)
    print(f"Saved summary to: {output_path}")

def main():
    print("=" * 60)
    print("EPSTEIN FILES DATA VISUALIZATION")
    print("=" * 60)

    # Load data
    embeddings_data = load_embeddings()

    # Create visualizations
    umap_df = create_umap_visualization(embeddings_data)
    network_stats = create_network_graph(embeddings_data)
    type_counts, volume_counts = create_document_distribution(embeddings_data)

    # Create summary
    create_summary(embeddings_data, network_stats, type_counts)

    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE!")
    print("=" * 60)
    print(f"\nOutput files in: {OUTPUT_DIR}")
    print("  - epstein_embedding_clusters.html")
    print("  - epstein_network_graph.html")
    print("  - epstein_doc_distribution.html")
    print("  - EPSTEIN_VISUALIZATIONS_SUMMARY.md")

if __name__ == "__main__":
    main()
