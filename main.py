#!/usr/bin/env python3
"""
Data Whisperer - OSINT Entity Extraction & Mapping Tool
Main CLI interface
"""

import argparse
import sys
from pathlib import Path
import json
from datetime import datetime

from datawhisperer.extractor import EntityExtractor
from datawhisperer.classify import EntityClassifier
from datawhisperer.export import ExportManager
from datawhisperer.rules import RelationshipEngine
from datawhisperer.mapbuilder import GraphBuilder
from datawhisperer.visualize import NetworkVisualizer
from datawhisperer.utils import read_from_clipboard, sanitize_text


def main():
    """Main entry point for Data Whisperer CLI"""
    
    parser = argparse.ArgumentParser(
        description='Data Whisperer - OSINT Entity Extraction & Mapping Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a text file and generate reports
  python main.py --input dump.txt --analyze --output results/
  
  # Analyze and create network visualization
  python main.py --input dump.txt --analyze --map
  
  # Read from clipboard and analyze
  python main.py --clipboard --analyze --map
  
  # Import existing JSON and create map
  python main.py --import entities.json --map
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Input text file to analyze'
    )
    input_group.add_argument(
        '--clipboard', '-c',
        action='store_true',
        help='Read input from clipboard'
    )
    input_group.add_argument(
        '--import',
        dest='import_json',
        type=str,
        help='Import previously exported JSON file'
    )
    
    # Action options
    parser.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Run entity extraction and classification'
    )
    parser.add_argument(
        '--map', '-m',
        action='store_true',
        help='Generate OSINT network map visualization'
    )
    parser.add_argument(
        '--no-dns',
        action='store_true',
        help='Disable DNS lookups for domain-to-IP relationships'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='Output directory (default: output/)'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        nargs='+',
        choices=['json', 'markdown', 'txt', 'html'],
        default=['json', 'markdown'],
        help='Output formats (default: json markdown)'
    )
    parser.add_argument(
        '--map-file',
        type=str,
        help='Custom filename for network map HTML (default: auto-generated)'
    )
    
    # Display options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    # Validate actions
    if not args.analyze and not args.map:
        parser.error("At least one action required: --analyze or --map")
    
    # Initialize components
    extractor = EntityExtractor()
    classifier = EntityClassifier()
    
    # Determine source name for better output file naming
    source_name = "analysis"
    
    classified_data = None
    
    try:
        # Step 1: Get input text
        if args.analyze:
            if args.input:
                if not args.quiet:
                    print(f"[*] Reading input file: {args.input}")
                
                input_path = Path(args.input)
                if not input_path.exists():
                    print(f"[!] Error: File not found: {args.input}", file=sys.stderr)
                    sys.exit(1)
                
                # Extract filename without extension for better output naming
                source_name = input_path.stem
                
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            
            elif args.clipboard:
                if not args.quiet:
                    print("[*] Reading from clipboard...")
                
                source_name = "clipboard"
                
                text = read_from_clipboard()
                if text is None:
                    print("[!] Error: Could not read from clipboard", file=sys.stderr)
                    sys.exit(1)
            
            # Step 2: Extract entities
            if not args.quiet:
                print("[*] Extracting entities...")
            
            entities = extractor.extract(text)
            
            if args.verbose:
                summary = extractor.get_summary()
                print(f"[+] Extracted {len(entities)} entities:")
                for entity_type, count in sorted(summary.items()):
                    print(f"    - {entity_type}: {count}")
            
            # Step 3: Classify and validate
            if not args.quiet:
                print("[*] Classifying and validating entities...")
            
            classified_data = classifier.classify(entities)
            
            if not args.quiet:
                print(f"[+] {classifier.get_summary_text()}")
            
            # Step 4: Build relationships
            if not args.quiet:
                print("[*] Building entity relationships...")
            
            relationship_engine = RelationshipEngine(enable_dns_lookup=not args.no_dns)
            relationships = relationship_engine.build_relationships(classified_data['entities'])
            classified_data['relationships'] = relationships
            
            if args.verbose:
                rel_summary = relationship_engine.get_relationship_summary()
                print(f"[+] Found {len(relationships)} relationships:")
                for rel_type, count in sorted(rel_summary.items()):
                    print(f"    - {rel_type}: {count}")
            
            # Step 5: Export data
            if not args.quiet:
                print(f"[*] Exporting results to: {args.output}/")
            
            # Initialize export manager with source name
            export_manager = ExportManager(output_dir=args.output, source_name=source_name)
            
            exported_files = []
            
            if 'json' in args.format:
                json_file = export_manager.export_json(classified_data)
                exported_files.append(json_file)
                if args.verbose:
                    print(f"    [+] JSON: {json_file}")
            
            if 'markdown' in args.format:
                md_file = export_manager.export_markdown(classified_data)
                exported_files.append(md_file)
                if args.verbose:
                    print(f"    [+] Markdown: {md_file}")
            
            if 'txt' in args.format:
                txt_file = export_manager.export_txt(classified_data)
                exported_files.append(txt_file)
                if args.verbose:
                    print(f"    [+] Text: {txt_file}")
            
            if 'html' in args.format:
                html_file = export_manager.export_html(classified_data)
                exported_files.append(html_file)
                if args.verbose:
                    print(f"    [+] HTML: {html_file}")
            
            if not args.quiet and not args.verbose:
                print(f"[+] Exported {len(exported_files)} files")
        
        # Step 6: Import existing JSON if specified
        elif args.import_json:
            if not args.quiet:
                print(f"[*] Importing JSON file: {args.import_json}")
            
            import_path = Path(args.import_json)
            if not import_path.exists():
                print(f"[!] Error: File not found: {args.import_json}", file=sys.stderr)
                sys.exit(1)
            
            # Extract source name from import filename
            source_name = import_path.stem
            
            with open(import_path, 'r', encoding='utf-8') as f:
                classified_data = json.load(f)
        
        # Step 7: Generate network map
        if args.map:
            if classified_data is None:
                print("[!] Error: No data to visualize. Run --analyze first or --import a JSON file.", file=sys.stderr)
                sys.exit(1)
            
            if not args.quiet:
                print("[*] Building network graph...")
            
            graph_builder = GraphBuilder()
            graph = graph_builder.build_graph(classified_data)
            
            graph_stats = graph_builder.get_graph_statistics()
            
            if args.verbose:
                print(f"[+] Graph statistics:")
                print(f"    - Nodes: {graph_stats['nodes']}")
                print(f"    - Edges: {graph_stats['edges']}")
                print(f"    - Density: {graph_stats['density']:.3f}")
                print(f"    - Connected components: {graph_stats['components']}")
            
            if not args.quiet:
                print("[*] Generating interactive visualization...")
            
            visualizer = NetworkVisualizer()
            
            # Determine output filename with source name
            if args.map_file:
                map_output = Path(args.output) / args.map_file
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                map_output = Path(args.output) / f"{source_name}_network_{timestamp}.html"
            
            map_path = visualizer.visualize(graph, str(map_output))
            
            if not args.quiet:
                print(f"[+] Network map saved to: {map_path}")
            
            # Export graph in other formats
            if args.verbose:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                graphml_path = Path(args.output) / f"{source_name}_graph_{timestamp}.graphml"
                graph_builder.export_graphml(str(graphml_path))
                print(f"    [+] GraphML: {graphml_path}")
                
                graph_json_path = Path(args.output) / f"{source_name}_graph_{timestamp}.json"
                graph_builder.export_json(str(graph_json_path))
                print(f"    [+] Graph JSON: {graph_json_path}")
        
        if not args.quiet:
            print("\n[✓] Data Whisperer completed successfully!")
            print(f"[✓] Results saved to: {args.output}/")
    
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        print(f"\n[!] Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

