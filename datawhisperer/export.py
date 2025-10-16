"""
Export module for various output formats
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ExportManager:
    """Manage exports in different formats"""
    
    def __init__(self, output_dir: str = "output", source_name: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.source_name = source_name or "analysis"
        
    def export_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export data as JSON
        
        Args:
            data: Data to export
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_entities_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def export_markdown(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export data as Markdown report
        
        Args:
            data: Classified data
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_report_{timestamp}.md"
        
        output_path = self.output_dir / filename
        
        # Generate markdown content
        md_content = self._generate_markdown(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(output_path)
    
    def export_txt(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export data as plain text summary
        
        Args:
            data: Classified data
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_summary_{timestamp}.txt"
        
        output_path = self.output_dir / filename
        
        # Generate text content
        txt_content = self._generate_text(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        return str(output_path)
    
    def export_html(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export data as HTML report
        
        Args:
            data: Classified data
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_report_{timestamp}.html"
        
        output_path = self.output_dir / filename
        
        # Generate HTML content
        html_content = self._generate_html(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        stats = data.get('statistics', {})
        entities = data.get('entities', [])
        groups = data.get('groups', {})
        relationships = data.get('relationships', [])
        
        md = []
        md.append("# Data Whisperer - Entity Analysis Report\n")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append("---\n")
        
        # Statistics
        md.append("## Summary Statistics\n")
        md.append(f"- **Total Entities:** {stats.get('total_entities', 0)}")
        md.append(f"- **Average Confidence:** {stats.get('confidence_avg', 0)}")
        md.append(f"- **High Confidence Entities:** {stats.get('high_confidence', 0)}")
        md.append(f"- **Validation Rate:** {stats.get('validation_rate', 0)}\n")
        
        # Entity counts by type
        md.append("### Entities by Type\n")
        by_type = stats.get('by_type', {})
        for entity_type, count in sorted(by_type.items()):
            md.append(f"- **{entity_type}:** {count}")
        md.append("")
        
        # Detailed entities
        md.append("## Extracted Entities\n")
        
        # Group by type for display
        entities_by_type = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        for entity_type, entity_list in sorted(entities_by_type.items()):
            md.append(f"### {entity_type.upper().replace('_', ' ')}\n")
            md.append("| Value | Confidence | Line | Context |")
            md.append("|-------|------------|------|---------|")
            
            for entity in entity_list[:50]:  # Limit to 50 per type
                value = entity['value']
                confidence = entity['confidence']
                line = entity['line']
                context = entity['context'][:50] + "..." if len(entity['context']) > 50 else entity['context']
                md.append(f"| `{value}` | {confidence} | {line} | {context} |")
            
            if len(entity_list) > 50:
                md.append(f"\n*({len(entity_list) - 50} more...)*")
            md.append("")
        
        # Relationships
        if relationships:
            md.append("## Relationships\n")
            md.append("| Type | Source | Target | Confidence |")
            md.append("|------|--------|--------|------------|")
            
            for rel in relationships[:100]:  # Limit to 100
                rel_type = rel['type']
                source = str(rel.get('source', 'N/A'))[:40]
                target = str(rel.get('target', 'N/A'))[:40]
                confidence = rel.get('confidence', 0)
                md.append(f"| {rel_type} | `{source}` | `{target}` | {confidence} |")
            md.append("")
        
        # Groups
        if groups.get('email_domains'):
            md.append("## Email Domains\n")
            for domain, emails in sorted(groups['email_domains'].items()):
                md.append(f"- **{domain}** ({len(emails)} emails)")
        
        if groups.get('url_domains'):
            md.append("\n## URL Domains\n")
            for domain, urls in sorted(groups['url_domains'].items()):
                md.append(f"- **{domain}** ({len(urls)} URLs)")
        
        md.append("\n---\n*Report generated by Data Whisperer*")
        
        return '\n'.join(md)
    
    def _generate_text(self, data: Dict[str, Any]) -> str:
        """Generate plain text summary"""
        stats = data.get('statistics', {})
        entities = data.get('entities', [])
        
        lines = []
        lines.append("=" * 60)
        lines.append("DATA WHISPERER - ENTITY ANALYSIS SUMMARY")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")
        
        # Statistics
        lines.append("SUMMARY STATISTICS")
        lines.append("-" * 60)
        lines.append(f"Total Entities: {stats.get('total_entities', 0)}")
        lines.append(f"Average Confidence: {stats.get('confidence_avg', 0)}")
        lines.append(f"High Confidence Entities: {stats.get('high_confidence', 0)}")
        lines.append(f"Validation Rate: {stats.get('validation_rate', 0)}")
        lines.append("")
        
        # Entity counts
        lines.append("ENTITIES BY TYPE")
        lines.append("-" * 60)
        by_type = stats.get('by_type', {})
        for entity_type, count in sorted(by_type.items()):
            lines.append(f"  {entity_type.ljust(20)}: {count}")
        lines.append("")
        
        # Top entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        lines.append("SAMPLE ENTITIES (Top 10 per type)")
        lines.append("-" * 60)
        for entity_type, entity_list in sorted(entities_by_type.items()):
            lines.append(f"\n{entity_type.upper()}:")
            for entity in entity_list[:10]:
                lines.append(f"  - {entity['value']} (confidence: {entity['confidence']})")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("End of Report")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def _generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        stats = data.get('statistics', {})
        entities = data.get('entities', [])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Whisperer - Entity Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .stat-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        
        table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        table tr:hover {{
            background: #f8f9fa;
        }}
        
        .entity-value {{
            font-family: 'Courier New', monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .confidence {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            background: #28a745;
            color: white;
            font-size: 0.85em;
        }}
        
        .confidence.medium {{
            background: #ffc107;
        }}
        
        .confidence.low {{
            background: #dc3545;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Data Whisperer</h1>
            <p>Entity Analysis Report - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Entities</h3>
                    <div class="value">{stats.get('total_entities', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3>Average Confidence</h3>
                    <div class="value">{stats.get('confidence_avg', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3>High Confidence</h3>
                    <div class="value">{stats.get('high_confidence', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3>Validation Rate</h3>
                    <div class="value">{stats.get('validation_rate', 0)}</div>
                </div>
            </div>
"""
        
        # Add entity tables by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        for entity_type, entity_list in sorted(entities_by_type.items()):
            html += f"""
            <div class="section">
                <h2>{entity_type.upper().replace('_', ' ')}</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Value</th>
                            <th>Confidence</th>
                            <th>Line</th>
                            <th>Context</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            for entity in entity_list[:50]:  # Limit to 50 per type
                conf_class = 'high' if entity['confidence'] >= 0.8 else ('medium' if entity['confidence'] >= 0.5 else 'low')
                context = entity['context'][:60] + '...' if len(entity['context']) > 60 else entity['context']
                
                html += f"""
                        <tr>
                            <td><span class="entity-value">{entity['value']}</span></td>
                            <td><span class="confidence {conf_class}">{entity['confidence']}</span></td>
                            <td>{entity['line']}</td>
                            <td>{context}</td>
                        </tr>
"""
            
            html += """
                    </tbody>
                </table>
            </div>
"""
        
        html += """
        </div>
        
        <div class="footer">
            <p>Report generated by Data Whisperer - OSINT Entity Extraction Tool</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html

