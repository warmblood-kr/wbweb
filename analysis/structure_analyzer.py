#!/usr/bin/env python3
"""
wbgpt Structure Analyzer

A reusable script to analyze wbgpt codebase structure and guide the extraction process.
This script systematically examines components, dependencies, and provides extraction recommendations.
"""

import os
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class ComponentInfo:
    """Information about a wbgpt component"""
    name: str
    path: Path
    imports: Set[str] = field(default_factory=set)
    internal_imports: Set[str] = field(default_factory=set)  # wbgpt internal imports
    external_imports: Set[str] = field(default_factory=set)  # third-party imports
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    has_business_logic: bool = False
    coupling_score: int = 0


class WbgptStructureAnalyzer:
    """Analyzes wbgpt structure for extraction planning"""
    
    def __init__(self, wbgpt_path: str = "/home/toracle/projects/wbgpt"):
        self.wbgpt_path = Path(wbgpt_path)
        self.core_path = self.wbgpt_path / "wbgpt" / "core"
        self.components: Dict[str, ComponentInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze(self) -> Dict:
        """Main analysis method"""
        print("🔍 Analyzing wbgpt structure...")
        
        if not self.core_path.exists():
            print(f"❌ Core path not found: {self.core_path}")
            return {}
            
        # Scan core components
        self._scan_core_components()
        
        # Analyze dependencies
        self._analyze_dependencies()
        
        # Calculate coupling scores
        self._calculate_coupling_scores()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return {
            "components": {name: self._component_to_dict(comp) 
                         for name, comp in self.components.items()},
            "dependency_graph": {k: list(v) for k, v in self.dependency_graph.items()},
            "recommendations": recommendations,
            "summary": self._generate_summary()
        }
    
    def _scan_core_components(self):
        """Scan wbgpt/core/ directory for components"""
        print(f"📁 Scanning {self.core_path}")
        
        for py_file in self.core_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            relative_path = py_file.relative_to(self.core_path)
            component_name = str(relative_path).replace("/", ".").replace(".py", "")
            
            print(f"  📄 Analyzing {component_name}")
            
            component = ComponentInfo(
                name=component_name,
                path=py_file
            )
            
            try:
                self._analyze_python_file(py_file, component)
                self.components[component_name] = component
            except Exception as e:
                print(f"  ⚠️  Error analyzing {component_name}: {e}")
    
    def _analyze_python_file(self, file_path: Path, component: ComponentInfo):
        """Analyze a single Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        component.lines_of_code = len([line for line in content.split('\n') if line.strip()])
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        component.imports.add(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        component.imports.add(node.module)
                        
                elif isinstance(node, ast.ClassDef):
                    component.classes.append(node.name)
                    
                elif isinstance(node, ast.FunctionDef):
                    component.functions.append(node.name)
                    
        except SyntaxError as e:
            print(f"    ⚠️  Syntax error in {file_path}: {e}")
        
        # Classify imports
        self._classify_imports(component)
        
        # Detect business logic
        self._detect_business_logic(component, content)
    
    def _classify_imports(self, component: ComponentInfo):
        """Classify imports as internal vs external"""
        for imp in component.imports:
            if imp.startswith("wbgpt"):
                component.internal_imports.add(imp)
            else:
                component.external_imports.add(imp)
    
    def _detect_business_logic(self, component: ComponentInfo, content: str):
        """Detect if component contains business-specific logic"""
        business_indicators = [
            "conversation", "message", "chat", "llm", "gpt", 
            "openai", "anthropic", "claude", "model", "prompt"
        ]
        
        content_lower = content.lower()
        component.has_business_logic = any(
            indicator in content_lower for indicator in business_indicators
        )
    
    def _analyze_dependencies(self):
        """Build dependency graph"""
        for name, component in self.components.items():
            for internal_import in component.internal_imports:
                # Extract the component part from import
                if internal_import.startswith("wbgpt.core."):
                    dep_name = internal_import.replace("wbgpt.core.", "")
                    if dep_name in self.components:
                        self.dependency_graph[name].add(dep_name)
    
    def _calculate_coupling_scores(self):
        """Calculate coupling scores for each component"""
        for name, component in self.components.items():
            # Count internal dependencies
            internal_deps = len(component.internal_imports)
            
            # Count how many components depend on this one
            dependents = sum(1 for deps in self.dependency_graph.values() 
                           if name in deps)
            
            # Simple coupling score: internal deps + dependents
            component.coupling_score = internal_deps + dependents
    
    def _generate_recommendations(self) -> Dict:
        """Generate extraction recommendations"""
        # Sort by coupling score (lower = easier to extract)
        sorted_components = sorted(
            self.components.values(),
            key=lambda c: (c.coupling_score, c.has_business_logic)
        )
        
        extraction_order = []
        for component in sorted_components:
            if not component.has_business_logic:
                extraction_order.append({
                    "name": component.name,
                    "coupling_score": component.coupling_score,
                    "reason": "Low coupling, no business logic",
                    "priority": "high" if component.coupling_score < 3 else "medium"
                })
        
        return {
            "extraction_order": extraction_order,
            "high_priority": [c for c in extraction_order if c["priority"] == "high"],
            "needs_cleanup": [
                {
                    "name": comp.name,
                    "reason": "Contains business logic that needs removal"
                }
                for comp in sorted_components if comp.has_business_logic
            ]
        }
    
    def _generate_summary(self) -> Dict:
        """Generate analysis summary"""
        total_components = len(self.components)
        generic_components = sum(1 for c in self.components.values() 
                               if not c.has_business_logic)
        business_components = total_components - generic_components
        
        return {
            "total_components": total_components,
            "generic_components": generic_components,
            "business_components": business_components,
            "extraction_ready": len([c for c in self.components.values() 
                                   if not c.has_business_logic and c.coupling_score < 3])
        }
    
    def _component_to_dict(self, component: ComponentInfo) -> Dict:
        """Convert ComponentInfo to dictionary"""
        return {
            "name": component.name,
            "path": str(component.path),
            "imports": list(component.imports),
            "internal_imports": list(component.internal_imports),
            "external_imports": list(component.external_imports),
            "classes": component.classes,
            "functions": component.functions,
            "lines_of_code": component.lines_of_code,
            "has_business_logic": component.has_business_logic,
            "coupling_score": component.coupling_score
        }
    
    def print_summary(self, results: Dict):
        """Print analysis summary"""
        summary = results["summary"]
        recommendations = results["recommendations"]
        
        print("\n" + "="*60)
        print("📊 WBGPT STRUCTURE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📁 Total components: {summary['total_components']}")
        print(f"🔧 Generic components: {summary['generic_components']}")
        print(f"💼 Business components: {summary['business_components']}")
        print(f"✅ Ready for extraction: {summary['extraction_ready']}")
        
        print("\n🎯 HIGH PRIORITY EXTRACTIONS:")
        for item in recommendations["high_priority"]:
            print(f"  • {item['name']} (coupling: {item['coupling_score']}) - {item['reason']}")
        
        print("\n🔧 NEEDS CLEANUP:")
        for item in recommendations["needs_cleanup"]:
            print(f"  • {item['name']} - {item['reason']}")


def main():
    """Main execution"""
    analyzer = WbgptStructureAnalyzer()
    results = analyzer.analyze()
    
    # Print summary
    analyzer.print_summary(results)
    
    # Save detailed results
    output_file = Path(__file__).parent / "wbgpt_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    main()