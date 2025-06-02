import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Set, Dict, Any
from core.point import Point
from core.map import Map

class Visualizer:
    """Handles visualization of results"""

    def __init__(self):
        pass

    def visualize_map(self, map_data: Map):
        """Visualize map with objects"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Plot objects
        for obj in map_data.objects:
            circle = patches.Circle((obj.x, obj.y), map_data.survey_radius,
                                    fill=False, color='lightblue', alpha=0.3)
            ax.add_patch(circle)
            ax.plot(obj.x, obj.y, 'bo', markersize=6)
            ax.annotate(obj.name, (obj.x, obj.y), xytext=(5, 5),
                        textcoords='offset points', fontsize=8)

        # Plot start and end points
        ax.plot(map_data.start_point.x, map_data.start_point.y, 'go', markersize=10, label='Start')
        ax.plot(map_data.end_point.x, map_data.end_point.y, 'ro', markersize=10, label='End')

        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axis('equal')
        ax.set_title('UAV Routing Task Map')

        plt.tight_layout()
        plt.show()

    def visualize_results(self, map_data: Map, route: List[Point], surveyed: Set[Point], solver_name: str, filename: str):
        """Visualize routing results"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Plot objects
        for obj in map_data.objects:
            color = 'lightgreen' if obj in surveyed else 'lightcoral'
            circle = patches.Circle((obj.x, obj.y), map_data.survey_radius,
                                    fill=False, color=color, alpha=0.5)
            ax.add_patch(circle)
            marker_color = 'green' if obj in surveyed else 'red'
            ax.plot(obj.x, obj.y, 'o', color=marker_color, markersize=6)

            status = "surveyed" if obj in surveyed else "missed"
            ax.annotate(f'{obj.name}\n({status})', (obj.x, obj.y),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, color=marker_color)

        # Plot route
        if len(route) > 1:
            route_x = [p.x for p in route]
            route_y = [p.y for p in route]
            ax.plot(route_x, route_y, 'b-', linewidth=2, label='Route')
            ax.plot(route_x, route_y, 'ko', markersize=4)

        # Plot start and end
        ax.plot(map_data.start_point.x, map_data.start_point.y, 'go', markersize=10, label='Start')
        ax.plot(map_data.end_point.x, map_data.end_point.y, 'ro', markersize=10, label='End')

        # Statistics
        total_distance = sum(route[i].distance_to(route[i + 1]) for i in range(len(route) - 1))
        coverage = len(surveyed) / len(map_data.objects) * 100 if map_data.objects else 0

        info_text = f"""Algorithm: {solver_name}
Objects surveyed: {len(surveyed)}/{len(map_data.objects)} ({coverage:.1f}%)
Route distance: {total_distance:.2f}
Max distance: {map_data.max_distance}
Used: {total_distance / map_data.max_distance * 100:.1f}%"""

        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=10)

        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axis('equal')
        ax.set_title(f'UAV Route - {solver_name} Algorithm')

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()


    def visualize_comparison(self, results: Dict[str, Any], filename: str):
        """Visualize comparison of different algorithms"""
        algorithms = list(results.keys())
        coverages = [r['coverage'] for r in results.values()]
        distances = [r['distance'] for r in results.values()]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Coverage comparison
        ax1.bar(algorithms, coverages, color=['blue', 'green'])
        ax1.set_ylabel('Coverage (%)')
        ax1.set_title('Coverage Comparison')
        ax1.set_ylim(0, 110)

        for i, v in enumerate(coverages):
            ax1.text(i, v + 2, f'{v:.1f}%', ha='center')

        # Distance comparison
        ax2.bar(algorithms, distances, color=['blue', 'green'])
        ax2.set_ylabel('Total Distance')
        ax2.set_title('Route Distance Comparison')

        for i, v in enumerate(distances):
            ax2.text(i, v + 2, f'{v:.1f}', ha='center')

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()


    def save_plot(self, filename: str):
        """Save current plot to file"""
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")

