#!/usr/bin/env python3
"""
Data Whisperer - Quick Start Script
Tests installation and runs sample analysis
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = [
        'tldextract',
        'phonenumbers',
        'dns.resolver',
        'networkx',
        'pyvis',
        'pyperclip'
    ]
    
    missing = []
    
    for module in required:
        try:
            if module == 'dns.resolver':
                __import__('dns.resolver')
            else:
                __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print("\n❌ Missing dependencies. Please run:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!\n")
    return True


def run_sample_analysis():
    """Run analysis on sample data"""
    print("🚀 Running sample analysis...\n")
    
    # Check if sample file exists
    sample_file = Path("examples/sample_dump.txt")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    # Import Data Whisperer modules
    try:
        from datawhisperer import EntityExtractor, EntityClassifier, GraphBuilder, NetworkVisualizer
        from datawhisperer.rules import RelationshipEngine
        from datawhisperer.export import ExportManager
    except ImportError as e:
        print(f"❌ Error importing Data Whisperer: {e}")
        return False
    
    # Read sample file
    with open(sample_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Step 1: Extract entities
    print("📊 Step 1: Extracting entities...")
    extractor = EntityExtractor()
    entities = extractor.extract(text)
    summary = extractor.get_summary()
    
    print(f"  Found {len(entities)} entities:")
    for entity_type, count in sorted(summary.items()):
        print(f"    • {entity_type}: {count}")
    
    # Step 2: Classify
    print("\n🎯 Step 2: Classifying and validating...")
    classifier = EntityClassifier()
    classified = classifier.classify(entities)
    
    stats = classified['statistics']
    print(f"  Total: {stats['total_entities']}")
    print(f"  Average confidence: {stats['confidence_avg']}")
    print(f"  High confidence: {stats['high_confidence']}")
    
    # Step 3: Build relationships
    print("\n🔗 Step 3: Building relationships...")
    rel_engine = RelationshipEngine(enable_dns_lookup=False)  # Disable DNS for speed
    relationships = rel_engine.build_relationships(classified['entities'])
    classified['relationships'] = relationships
    
    rel_summary = rel_engine.get_relationship_summary()
    print(f"  Found {len(relationships)} relationships:")
    for rel_type, count in sorted(rel_summary.items()):
        print(f"    • {rel_type}: {count}")
    
    # Step 4: Export
    print("\n💾 Step 4: Exporting results...")
    export_manager = ExportManager(output_dir="output", source_name="quick_start")
    
    json_file = export_manager.export_json(classified)
    print(f"  ✓ JSON: {json_file}")
    
    md_file = export_manager.export_markdown(classified)
    print(f"  ✓ Markdown: {md_file}")
    
    # Step 5: Build graph
    print("\n🌐 Step 5: Building network graph...")
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(classified)
    
    graph_stats = graph_builder.get_graph_statistics()
    print(f"  Nodes: {graph_stats['nodes']}")
    print(f"  Edges: {graph_stats['edges']}")
    print(f"  Density: {graph_stats['density']:.3f}")
    
    # Step 6: Visualize
    print("\n🎨 Step 6: Creating visualization...")
    visualizer = NetworkVisualizer()
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_file = visualizer.visualize(graph, f"output/quick_start_network_{timestamp}.html")
    print(f"  ✓ Network map: {map_file}")
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Data Whisperer is working correctly!")
    print("="*60)
    print("\n📂 Results saved to: output/")
    print("🌐 Open the network map in your browser:")
    print(f"   {Path(map_file).absolute()}")
    print("\n📖 Next steps:")
    print("   • Read USAGE_GUIDE.md for detailed examples")
    print("   • Try: python main.py --input your_file.txt --analyze --map")
    print("   • Check the Python API in README.md")
    
    return True


def main():
    """Main entry point"""
    print("="*60)
    print("🔍 DATA WHISPERER - Quick Start")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run sample analysis
    if not run_sample_analysis():
        sys.exit(1)
    
    print()


if __name__ == '__main__':
    main()

