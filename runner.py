import os.path
from typing import List, Dict
import argparse
from datetime import datetime
import random

from data.data_manager import DataManager
from data.visualizer import Visualizer
from data.data_generator import DataGenerator
from core.greedy import GreedySolver
from core.heuristic import HeuristicSolver
from core.map import Map


class Runner:
    """Main runner class for the application"""

    def __init__(self):
        self.data_generator = DataGenerator()
        self.data_manager = DataManager()
        self.visualizer = Visualizer()
        self.solvers = {
            'greedy': GreedySolver,
            'heuristic': HeuristicSolver
        }
        self.path = os.path.join("data", "output") # "data/output"
        self.output = str(max((int(f) for f in os.listdir(self.path) if f.isdigit() and os.path.isdir(os.path.join(self.path, f))),
                  default=0) + 1)

        os.makedirs(os.path.join(self.path, self.output), exist_ok=True)

    def run_single_experiment(self, map_data: Map) -> Dict:
        """Run experiment with single map"""
        results = {}

        for name, solver_class in self.solvers.items():
            print(f"\nRunning {name} algorithm...")
            solver = solver_class(map_data)

            import time
            start_time = time.time()
            route, surveyed, distance = solver.solve()
            end_time = time.time()

            coverage = len(surveyed) / len(map_data.objects) * 100 if map_data.objects else 0

            results[name] = {
                'route': route,
                'surveyed_objects': surveyed,
                'distance': distance,
                'coverage': coverage,
                'computation_time': end_time - start_time
            }

            print(f"  Completed in {end_time - start_time:.3f}s")
            print(f"  Coverage: {coverage:.1f}%")

        return results

    def run_batch_experiments(self, test_suite: List[Map]) -> List[Dict]:
        """Run experiments on multiple maps"""
        all_results = []

        for i, map_data in enumerate(test_suite):
            print(f"\nProcessing map {i + 1}/{len(test_suite)}...")
            results = self.run_single_experiment(map_data)
            results['map_index'] = i
            all_results.append(results)

        return all_results

    def compare_algorithms(self, map_data: Map, i: int) -> Dict:
        """Compare different algorithms on the same map"""
        results = self.run_single_experiment(map_data)

        # Visualize each algorithm's results
        for name, data in results.items():
            if isinstance(data, dict) and 'route' in data:
                self.visualizer.visualize_results(
                    map_data, data['route'], data['surveyed_objects'], name.upper(),
                    os.path.join(self.path, self.output, f"{name}_{i}.png")
                )

        # Show comparison
        self.visualizer.visualize_comparison(results, os.path.join(self.path, self.output, f"compare_{i}.png"))


        return results

    def main(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(description='UAV Route Optimization')
        parser.add_argument('--algorithm', choices=['greedy', 'heuristic', 'all'],
                            default='all', help='Algorithm to use')
        parser.add_argument('--generate', action='store_true',
                            help='Generate new test data')
        parser.add_argument('-n', '--number', type=int, default=5,
                            help='Number of test cases to generate')
        parser.add_argument('--file', action='store_true',
                            help='Use existing files from input directory')

        args = parser.parse_args()

        # Determine which algorithms to run
        if args.algorithm == 'all':
            active_solvers = self.solvers
        else:
            active_solvers = {args.algorithm: self.solvers[args.algorithm]}

        self.solvers = active_solvers

        # Get maps to process
        maps_to_process = []

        if args.file:
            # Load from files
            files = self.data_manager.list_input_files()
            if not files:
                print("No input files found. Generating sample data...")
                # Generate one sample
                sample_map = self.data_generator.generate_single_task(10, 150, 10)
                self.data_manager.save_map_to_file(sample_map, "sample_map.json")
                maps_to_process.append(sample_map)
            else:
                print(f"Found {len(files)} input files")
                for file in files[:args.number]:  # Limit to requested number
                    map_data = self.data_manager.load_map_from_file(file)
                    maps_to_process.append(map_data)

        elif args.generate:
            # Generate new maps
            print(f"Generating {args.number} test cases...")
            for i in range(args.number):
                n_objects = random.randint(30, 35)
                max_distance = random.choice(self.data_generator.distance_options)
                survey_radius = random.uniform(5, 15)

                map_data = self.data_generator.generate_single_task(
                    n_objects, max_distance, survey_radius
                )

                # Save generated map
                filename = f"generated_map_{i + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.data_manager.save_map_to_file(map_data, filename)
                maps_to_process.append(map_data)

        else:
            print("Please specify --file or --generate option")
            return

        # Process all maps
        print(f"\nProcessing {len(maps_to_process)} maps with {list(active_solvers.keys())} algorithm(s)...")

        for i, map_data in enumerate(maps_to_process):
            print(f"\n{'=' * 60}")
            print(f"Processing Map {i + 1}/{len(maps_to_process)}")
            print(f"{'=' * 60}")
            print(f"Objects: {len(map_data.objects)}")
            print(f"Max distance: {map_data.max_distance}")
            print(f"Survey radius: {map_data.survey_radius}")

            # Validate map
            if not map_data.validate():
                print("Warning: Map validation failed, skipping...")
                continue

            # Run experiments
            results = self.compare_algorithms(map_data, i)

            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_filename = f"results_map_{i + 1}_{timestamp}.json"

            self.data_manager.save_results_to_file(results, os.path.join(self.output, results_filename))


            # Print results
            self.data_manager.print_results_to_console(results)

        print("\nAll tasks completed!")