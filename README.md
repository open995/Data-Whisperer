# 🔍 Data Whisperer

**Professional OSINT Entity Extraction & Network Mapping Tool**

Data Whisperer is an open-source intelligence (OSINT) tool that automatically extracts, classifies, and visualizes entities from unstructured text dumps. It transforms messy logs, pastebins, and raw data into structured reports and interactive network maps showing entity relationships.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🧠 Core Entity Extraction

Automatically detects and extracts:

- **Contact Information**: Emails, phone numbers, domains
- **Network Indicators**: IPv4/IPv6 addresses, URLs
- **Cryptographic Hashes**: MD5, SHA1, SHA256, SHA512
- **Cryptocurrency**: Bitcoin & Ethereum wallet addresses
- **Credentials**: Username:password patterns, API keys, JWT tokens

### 🎯 Smart Classification

- **Validation Engine**: Reduces false positives with intelligent format checking
- **Confidence Scoring**: Each entity gets a confidence score (0-1)
- **Contextual Metadata**: Line numbers, text snippets, detection methods
- **Relationship Extraction**: Automatically links related entities

### 🌐 OSINT Network Mapping

- **Interactive Visualizations**: Zoomable, pannable HTML network graphs
- **Relationship Discovery**: Automatically connects emails ↔ domains, domains ↔ IPs
- **DNS Enrichment**: Optional live DNS lookups for domain-to-IP mapping
- **Community Detection**: Identifies entity clusters and communities
- **Multiple Export Formats**: HTML, JSON, GraphML for further analysis

### 📊 Multi-Format Export

- **JSON**: Machine-readable structured data
- **Markdown**: Human-readable reports with statistics
- **TXT**: Plain text summaries
- **HTML**: Beautiful styled reports with tables and metrics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd whisper

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Analyze a text file
python main.py --input dump.txt --analyze

# Analyze and create network map
python main.py --input dump.txt --analyze --map

# Read from clipboard
python main.py --clipboard --analyze --map

# Import existing JSON and visualize
python main.py --import entities.json --map
```

### Example Workflow

```bash
# Full analysis with all export formats
python main.py \
  --input examples/sample_dump.txt \
  --analyze \
  --map \
  --format json markdown txt html \
  --output results/ \
  --verbose
```

## 📖 Usage Guide

### Command Line Options

#### Input Options (choose one)
- `--input <file>`, `-i`: Analyze a text file
- `--clipboard`, `-c`: Read from clipboard
- `--import <json>`: Import previously exported JSON

#### Actions (at least one required)
- `--analyze`, `-a`: Run entity extraction and classification
- `--map`, `-m`: Generate network visualization

#### Output Options
- `--output <dir>`, `-o`: Output directory (default: `output/`)
- `--format <formats>`, `-f`: Export formats: `json`, `markdown`, `txt`, `html` (default: `json markdown`)
- `--map-file <name>`: Custom filename for network map HTML

#### Additional Options
- `--no-dns`: Disable DNS lookups (faster, but fewer relationships)
- `--verbose`, `-v`: Detailed output
- `--quiet`, `-q`: Minimal output

### Python API

```python
from datawhisperer import EntityExtractor, EntityClassifier, GraphBuilder, NetworkVisualizer

# Extract entities
extractor = EntityExtractor()
entities = extractor.extract(text)

# Classify and validate
classifier = EntityClassifier()
classified = classifier.classify(entities)

# Build network graph
graph_builder = GraphBuilder()
graph = graph_builder.build_graph(classified)

# Visualize
visualizer = NetworkVisualizer()
visualizer.visualize(graph, "network.html")
```

## 📁 Project Structure

```
whisper/
├── datawhisperer/
│   ├── __init__.py          # Package initialization
│   ├── extractor.py         # Entity extraction with regex patterns
│   ├── classify.py          # Validation and classification
│   ├── export.py            # Multi-format export system
│   ├── rules.py             # Relationship detection rules
│   ├── mapbuilder.py        # NetworkX graph construction
│   ├── visualize.py         # PyVis network visualization
│   └── utils.py             # Helper functions
├── examples/
│   └── sample_dump.txt      # Sample data for testing
├── tests/
│   └── test_entities.py     # Unit tests
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎨 Entity Types & Colors

The network visualization uses color-coding for different entity types:

| Entity Type | Color | Description |
|------------|-------|-------------|
| Email | 🔴 Red | Email addresses |
| IPv4 | 🔵 Teal | IPv4 addresses |
| IPv6 | 🔵 Blue | IPv6 addresses |
| URL | 🟠 Salmon | Web URLs |
| Domain | 🟢 Mint | Domain names |
| Hashes | 🟡 Yellow/Orange | MD5, SHA1, SHA256, SHA512 |
| Bitcoin | 🟡 Gold | Bitcoin wallet addresses |
| Ethereum | 🟣 Purple | Ethereum wallet addresses |
| Phone | 🔵 Blue | Phone numbers |
| Credential | 🔴 Red | Username:password pairs |
| API Key | 🟣 Purple | API keys and tokens |

## 🔗 Relationship Types

Data Whisperer automatically detects these relationships:

- **email_to_domain**: Email address → its domain
- **url_to_domain**: URL → extracted domain
- **domain_to_ip**: Domain → resolved IP address (DNS lookup)
- **shared_domain**: Entities sharing the same domain
- **shared_ip**: Domains resolving to the same IP
- **credential_to_email**: Credentials matching email addresses

## 📊 Example Output

### Summary Statistics
```
Found: 15 email(s), 8 ipv4(s), 12 url(s), 3 md5(s)
Total entities: 38
Average confidence: 0.87
High confidence entities: 32
```

### Network Graph Statistics
```
Nodes: 38
Edges: 52
Density: 0.074
Connected components: 3
Average degree: 2.74
```

## 🛠️ Advanced Features

### DNS Enrichment

Enable DNS lookups to automatically resolve domains to IP addresses:

```bash
python main.py --input dump.txt --analyze --map
```

Disable DNS lookups for faster processing:

```bash
python main.py --input dump.txt --analyze --map --no-dns
```

### Graph Analysis

The tool calculates various network metrics:

- **Degree Centrality**: How connected each entity is
- **Betweenness Centrality**: Entities bridging different clusters
- **Community Detection**: Automatic grouping of related entities

### Custom Visualization

Interactive features in the HTML network map:

- **Zoom & Pan**: Mouse scroll to zoom, drag to pan
- **Node Interaction**: Click nodes for details, hover for tooltips
- **Dynamic Layout**: Physics-based automatic positioning
- **Dark Mode**: Professional dark theme for better visibility

## 🧪 Testing

Sample test file included:

```bash
python main.py --input examples/sample_dump.txt --analyze --map --verbose
```

Run unit tests:

```bash
pytest tests/
```

## 🔮 Future Enhancements

Potential additions for future versions:

- [ ] Streamlit GUI for interactive analysis
- [ ] AI-powered pattern summarization
- [ ] Multi-dump comparison and diffing
- [ ] Real-time API endpoint for automation
- [ ] Additional entity types (MAC addresses, file paths, etc.)
- [ ] Import/export from threat intelligence platforms
- [ ] Collaborative investigation features
- [ ] Custom rule builder for relationships

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📝 License

This project is open-source and available under the MIT License.

## ⚠️ Disclaimer

Data Whisperer is designed for legitimate OSINT research and digital forensics. Always ensure you have proper authorization before analyzing data. I am not responsible for misuse of this tool.

## 🙏 Acknowledgments

Built with:
- [NetworkX](https://networkx.org/) - Graph analysis
- [PyVis](https://pyvis.readthedocs.io/) - Network visualization
- [tldextract](https://github.com/john-kurkowski/tldextract) - Domain parsing
- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) - Phone number parsing
- [dnspython](https://www.dnspython.org/) - DNS lookups

---

**for OSINT researchers and digital forensics professionals**

