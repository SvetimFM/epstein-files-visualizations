# Methodology

## Data Source

**Source**: House Oversight Committee Epstein Files (November 2025 Release)
**Document Count**: 68,798 text chunks from ~10,000+ original documents
**Formats**: PDF (OCR'd images), text files, email exports

## Processing Pipeline

### 1. Document Chunking
- Documents split into ~2000 character chunks with 200 char overlap
- Chunk boundaries attempt to respect paragraph/sentence breaks
- Very large documents (>50 pages) may have chunking artifacts

### 2. Named Entity Recognition (NER)

**Model**: Claude 3 Haiku via AWS Bedrock
**Extraction Schema**:
```json
{
  "persons": ["name", "role/title", "context"],
  "organizations": ["name", "type", "context"],
  "locations": ["name", "type", "context"],
  "dates": ["date", "event", "participants"],
  "financial": ["amount", "parties", "purpose", "date"],
  "relationships": ["entity1", "entity2", "type", "context"]
}
```

**Batch Processing**: AWS Lambda with 50-document batches

### 3. Entity Deduplication

**Method**: Fuzzy string matching using rapidfuzz library
**Algorithm**:
- Blocking by first character for performance
- Cosine similarity on character n-grams
- Union-find clustering at 85% threshold

**Results**:
- Persons: 29,885 raw → 4,709 clustered identities (84% reduction)
- Organizations: 14,067 raw entities
- Locations: 9,539 raw entities

### 4. Embedding Generation

**Models Used**:
- AWS Titan Embed Text v1 (1536 dimensions) - initial processing
- Ollama nomic-embed-text (768 dimensions) - local validation

**Dimensionality Reduction**: UMAP
- n_neighbors: 15
- min_dist: 0.1
- metric: cosine
- random_state: 42 (reproducibility)

## Visualization Stack

| Visualization | Library | Notes |
|--------------|---------|-------|
| Entity Network | D3.js v7 | Force-directed, 800 nodes max |
| Timeline | D3.js v7 | Brush selection, 5000 events |
| Embedding Clusters | Plotly.js | UMAP 2D projection |
| Location Map | Leaflet + OpenStreetMap | Geocoded via nominatim |
| Entity Explorer | Vanilla JS | Searchable table |

## Known Limitations & Caveats

### NER Quality Issues

1. **Name Fragmentation**: Same person may appear under multiple variants (e.g., "Bill Clinton", "President Clinton", "WJC"). Deduplication catches ~84% but not all.

2. **False Positives**: NER sometimes extracts non-entities:
   - Legal boilerplate text interpreted as names
   - Redaction markers ("[REDACTED]") counted
   - OCR errors creating phantom entities

3. **Context Loss**: Chunking can split relevant context across boundaries, leading to incomplete relationship extraction.

### Data Completeness

1. **OCR Quality**: Image-based PDFs have variable OCR quality. Handwritten documents largely unreadable.

2. **Redactions**: Original documents contain heavy redactions. These appear as gaps in extracted data.

3. **Temporal Bias**: More recent documents (2000s-2020s) are better digitized than older ones.

### Visualization Limitations

1. **Network Graph**: Limited to top 800 entities by mention count. Long-tail entities not shown.

2. **Timeline**: Only includes events with parseable dates (1990-2025). ~40% of date mentions couldn't be parsed.

3. **Location Map**: Only shows locations that could be geocoded. Addresses like "the apartment" or "the island" may map incorrectly.

4. **Financial Records**: Dollar amounts may include OCR errors. Not all transactions have complete metadata.

## What This Is NOT

- **Not a complete record**: This represents extracted data from publicly released documents only
- **Not verified**: Extracted entities and relationships have not been fact-checked
- **Not accusatory**: Presence in these documents does not imply wrongdoing
- **Not exhaustive**: Many documents remain unreleased or heavily redacted

## Reproducibility

Code available at: https://github.com/SvetimFM/epstein-files-visualizations

Key files:
- `generate_visualizations.py` - Main visualization generator
- `epstein_visualizations.py` - Embedding cluster generation
- `cluster_names.py` - Entity deduplication

## Entity Statistics

| Category | Raw Count | After Dedup |
|----------|-----------|-------------|
| Document Chunks | 68,798 | - |
| Persons | 29,885 | 4,709 |
| Organizations | 14,067 | ~8,000* |
| Locations | 9,539 | ~6,000* |
| Timeline Events | 24,712 | - |
| Financial Records | 16,169 | - |
| Relationships | 10,004 | - |

*Approximate - org/location dedup less aggressive

## Victim Privacy

Known victim names have been redacted from public visualizations. The list of protected names is not published to prevent re-identification attempts.

---

*Generated November 2025 | NER: Claude 3 Haiku via AWS Bedrock*
