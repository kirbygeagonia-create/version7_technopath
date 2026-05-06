"""
Management command to auto-connect nearby navigation nodes.

This command creates NavigationEdge records between nodes that are close to each other,
forming a connected navigation graph. This is useful when nodes exist but edges haven't
been explicitly defined.

Usage:
    python manage.py auto_connect_nodes [--max-distance <meters>] [--floor <floor_num>]
"""

import math
from django.core.management.base import BaseCommand, CommandError
from apps.navigation.models import NavigationNode, NavigationEdge


class Command(BaseCommand):
    help = 'Auto-connect nearby navigation nodes to create a connected graph'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-distance',
            type=float,
            default=300.0,
            help='Maximum distance in meters to connect nodes (default: 300)'
        )
        parser.add_argument(
            '--floor',
            type=int,
            default=None,
            help='Only connect nodes on a specific floor (optional)'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creating edges if one already exists between nodes'
        )

    def handle(self, *args, **options):
        max_distance = options['max_distance']
        floor = options['floor']
        skip_existing = options['skip_existing']

        self.stdout.write(f"Auto-connecting navigation nodes...")
        self.stdout.write(f"Max distance: {max_distance}m")
        if floor:
            self.stdout.write(f"Floor: {floor}")

        # Get all non-deleted nodes
        nodes_query = NavigationNode.objects.filter(is_deleted=False)
        if floor:
            nodes_query = nodes_query.filter(floor=floor)

        nodes = list(nodes_query)
        self.stdout.write(f"Found {len(nodes)} nodes\n")

        if len(nodes) < 2:
            raise CommandError('Need at least 2 nodes to create edges')

        edges_created = 0
        edges_skipped = 0
        edges_failed = 0

        # Connect each node to nearby nodes
        for i, from_node in enumerate(nodes):
            self.stdout.write(f"Processing {from_node.name}...")

            for to_node in nodes:
                if from_node.id == to_node.id:
                    continue  # Skip self-connections

                # Check if edge already exists
                existing_edge = NavigationEdge.objects.filter(
                    from_node=from_node,
                    to_node=to_node,
                    is_deleted=False
                ).first()

                if existing_edge:
                    if skip_existing:
                        continue
                    else:
                        edges_skipped += 1
                        continue

                # Calculate distance between nodes
                distance = self._calculate_distance(from_node, to_node)

                if distance <= max_distance:
                    try:
                        NavigationEdge.objects.create(
                            from_node=from_node,
                            to_node=to_node,
                            distance=int(distance),
                            is_bidirectional=True
                        )
                        edges_created += 1
                        self.stdout.write(
                            f"  ✓ Connected to {to_node.name} ({distance:.1f}m)"
                        )
                    except Exception as e:
                        edges_failed += 1
                        self.stdout.write(
                            self.style.WARNING(f"  ✗ Failed to connect {to_node.name}: {e}")
                        )

            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(f"Edges created: {edges_created}")
        self.stdout.write(f"Edges skipped: {edges_skipped}")
        self.stdout.write(f"Edges failed: {edges_failed}")

        total_edges = NavigationEdge.objects.filter(is_deleted=False).count()
        self.stdout.write(f"Total edges now: {total_edges}")

        self.stdout.write(self.style.SUCCESS('\nAuto-connection complete!'))

    def _calculate_distance(self, node1, node2):
        """
        Calculate Euclidean distance between two nodes.
        Nodes have x, y coordinates in 0-1 range (SVG normalized coords).
        Assuming a standard campus is ~1000x1000 meters, we scale accordingly.
        """
        # Assuming normalized coordinates (0-1) correspond to actual canvas dimensions
        # For a typical campus map, we estimate 100x100 on the canvas = ~1000m
        scale_factor = 1000.0  # 1 unit in normalized coords = ~1000m

        dx = (node2.x - node1.x) * scale_factor
        dy = (node2.y - node1.y) * scale_factor

        distance = math.sqrt(dx**2 + dy**2)
        return distance
