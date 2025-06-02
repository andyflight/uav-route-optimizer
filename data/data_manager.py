from datetime import datetime
from typing import List, Dict
import json
import os
from core.point import Point
from core.map import Map
from data.visualizer import Visualizer

class DataManager:
    """Handles data input/output operations"""

    def __init__(self, input_dir: str = "data/input", output_dir: str = "data/output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.create_directories()


    def save_map_to_file(self, map_data: Map, filename: str):
        """Save map data to JSON file"""
        filepath = os.path.join(self.input_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(map_data.to_dict(), f, indent=2)
        print(f"Map saved to {filepath}")

    def load_map_from_file(self, filename: str) -> Map:
        """Load map data from JSON file"""
        filepath = os.path.join(self.input_dir, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Map.from_dict(data)

    def save_results_to_file(self, results: Dict, filename: str):
        """Save results to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        file_dir = "/".join(filepath.split("/")[:3])
        os.makedirs(file_dir, exist_ok=True)

        # Convert complex objects to serializable format
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_results[key] = {
                    'route': [p.to_dict() for p in value['route']],
                    'surveyed_objects': [p.to_dict() for p in value['surveyed_objects']],
                    'distance': value['distance'],
                    'coverage': value['coverage'],
                    'computation_time': value.get('computation_time', 0)
                }
            else:
                serializable_results[key] = value

        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"Results saved to {filepath}")

    def load_results_from_file(self, filename: str) -> Dict:
        """Load results from JSON file"""

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Convert back to objects
        results = {}
        for key, value in data.items():
            if isinstance(value, dict) and 'route' in value:
                results[key] = {
                    'route': [Point.from_dict(p) for p in value['route']],
                    'surveyed_objects': set(Point.from_dict(p) for p in value['surveyed_objects']),
                    'distance': value['distance'],
                    'coverage': value['coverage'],
                    'computation_time': value.get('computation_time', 0)
                }
            else:
                results[key] = value

        return results

    def print_results_to_console(self, results: Dict):
        """Print results to console in a formatted way"""
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)

        for algorithm, data in results.items():
            print(f"\n{algorithm.upper()} ALGORITHM:")
            print(f"  Objects surveyed: {len(data['surveyed_objects'])}")
            print(f"  Coverage: {data['coverage']:.1f}%")
            print(f"  Total distance: {data['distance']:.2f}")
            print(f"  Computation time: {data.get('computation_time', 0):.3f}s")

            if 'route' in data:
                print(f"  Route points: {len(data['route'])}")

        print("\n" + "=" * 60)

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def list_input_files(self) -> List[str]:
        """List all JSON files in input directory"""
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.json')]
        return sorted(files)