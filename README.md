# Epstein Files Visualizations

Interactive data visualizations and analysis of the November 2025 House Oversight Committee Epstein document release.

## Live Demo

**[View Visualizations](https://boxesblue.github.io/epstein-files-visualizations/)**

## Contents

### Visualizations
- **Embedding Cluster Map** - UMAP projection of 10,000 document embeddings showing semantic clusters
- **Network Graph** - Co-occurrence network of 31 named entities with 110 connections
- **Document Distribution** - Breakdown by document type and volume

### Reports
- **[RAG Mining Report](EPSTEIN_FILES_RAG_MINING_REPORT.md)** - Comprehensive findings with fact-checking, source citations, and novelty classifications
- **[Visualization Summary](EPSTEIN_VISUALIZATIONS_SUMMARY.md)** - Statistics and methodology

## Dataset

- **Total Documents:** 69,290 chunks
- **Embedding Model:** Ollama nomic-embed-text (768-dim)
- **Source:** House Oversight Committee Epstein Document Release (November 2025)

### HuggingFace
- [BoxesBlue/epstein-files-nov11-25-house-post-ocr-embeddings](https://huggingface.co/datasets/BoxesBlue/epstein-files-nov11-25-house-post-ocr-embeddings) - Full embeddings dataset
- [tensonaut/EPSTEIN_FILES_20K](https://huggingface.co/datasets/tensonaut/EPSTEIN_FILES_20K) - Original OCR'd documents

## Key Findings

### Most Significant Novel Revelation
**Chomsky extended timeline through May 2019** - Communications documented through May 26, 2019 (weeks before July arrest), including December 2018 "all in" quote for documentary project.

### Genuinely Novel
- Barry J. Cohen / JEGE Inc correspondence (October 2017)
- Nobel Charitable Trust Symposium (September 10, 2010)
- Seminar-POWER guest list specifics

### Requires Caveat
- $35M Harvard donation claim (actual was $6.5M per Harvard investigation)
- Some operational details were already publicly known (Visoski testimony 2021, etc.)

See [RAG Mining Report](EPSTEIN_FILES_RAG_MINING_REPORT.md) for full details.

## Technical Details

### Visualization Pipeline
```python
# Generate visualizations
python epstein_visualizations.py
```

### Dependencies
- `umap-learn` - Dimensionality reduction
- `plotly` - Interactive visualizations
- `networkx` - Graph analysis
- `pandas` - Data manipulation

## Important Note

These documents include both verified law enforcement records AND Epstein's own promotional materials. Cross-reference all findings with independent sources.

## License

Data is from public government document releases. Visualizations and analysis are provided for research purposes.

---

*Generated November 2025*
