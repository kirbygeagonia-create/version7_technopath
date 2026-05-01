# SEAIT_Map0.1.svg - Navigation Guide

## File Locations
- **Main File**: `frontend/src/assets/SEAIT_Map0.1.svg`
- **Backup**: `frontend/src/assets/SEAIT_Map0.1_BACKUP.svg`
- **Public Copy**: `frontend/public/SEAIT_Map0.1.svg`

## Navigation Nodes (IDs)

### Buildings (Blue - #07337B)
| ID | Position | Description |
|----|----------|-------------|
| `tailoring` | x=532.5, y=5186.5 | Tailoring Shop |
| `cl1_building` | x=532.5, y=5771.5 | CL1 Building |
| `cl2_building` | x=532.5, y=5975.5 | CL2 Building |
| `cl3_building` | x=532.5, y=6207.5 | CL3 Building |
| `cl4_building` | x=532.5, y=6439.5 | CL4 Building |
| `cl5_building` | x=768.5, y=5186.5 | CL5 Building |
| `main_hall` | x=1476.5, y=5186.5 | Main Hall |
| `central_building` | x=949.5, y=5186.5 | Central Building |
| `admin_building` | x=2896.5, y=6661.5 | Admin Building |
| `library` | x=1453.5, y=6054.5 | Library |
| `building_start` | x=396.5, y=5082.5 | Lower Campus Building |
| `building_end` | x=2855.5, y=1013.5 | Upper Campus Building |

### Waypoints - Blue (#2196F3)
| ID | Position | Description |
|----|----------|-------------|
| `college_gate` | x=238, y=4546 | Main Entrance |
| `point1` | cx=650, cy=4556 | Main Road Point 1 |
| `point2` | cx=650, cy=5186 | Near Tailoring |
| `cl1_entrance` | cx=650, cy=5771 | CL1 Entrance |
| `cl2_entrance` | cx=650, cy=5975 | CL2 Entrance |
| `cl3_entrance` | cx=650, cy=6207 | CL3 Entrance |
| `cl4_entrance` | cx=650, cy=6439 | CL4 Entrance |
| `main_intersection` | cx=1500, cy=4556 | Main Intersection |
| `library_entrance` | cx=1650, cy=6054 | Library Entrance |
| `admin_entrance` | cx=3050, cy=6661 | Admin Entrance |

### Waypoints - Orange (#FF9800) - NEW PATH
| ID | Position | Description |
|----|----------|-------------|
| `start_to_road` | cx=525, cy=4556 | From building_start to road |
| `road_east_1` | cx=1000, cy=4556 | East on main road |
| `road_east_2` | cx=1500, cy=4556 | Continue east |
| `road_east_3` | cx=2000, cy=4556 | Continue east |
| `road_east_4` | cx=2500, cy=4556 | Near east end |
| `upper_turn` | cx=2800, cy=3500 | Turn north |
| `upper_path_1` | cx=2850, cy=2500 | North path |
| `upper_path_2` | cx=2870, cy=1500 | Continue north |
| `end_approach` | cx=2879, cy=1200 | Approach building_end |

## Predefined Paths

### 1. College Gate to Tailoring
```javascript
['college_gate', 'point1', 'point2', 'tailoring']
```

### 2. Lower Campus to Upper Campus (NEW)
```javascript
['building_start', 'start_to_road', 'road_east_1', 'road_east_2', 
 'road_east_3', 'road_east_4', 'upper_turn', 'upper_path_1', 
 'upper_path_2', 'end_approach', 'building_end']
```

## How to Add New Navigation Nodes

1. Open `frontend/src/assets/SEAIT_Map0.1.svg`
2. Add a circle element with a unique ID:
```xml
<circle id="your_node_id" cx="X" cy="Y" r="25" 
        fill="none" stroke="#FF9800" stroke-width="3"/>
```
3. Copy the updated SVG to `frontend/public/SEAIT_Map0.1.svg`
4. Add the path in Admin Panel → SVG Paths

## SVG Dimensions
- **Width**: 3306
- **Height**: 7159
- **ViewBox**: 0 0 3306 7159

## Color Coding
- **#07337B** - Buildings (dark blue)
- **#0359C9** - Other structures (blue)
- **#2196F3** - Navigation waypoints (light blue circles)
- **#FF9800** - New path waypoints (orange circles)
- **#00B326** - Green areas
- **#9E9E9E** - Roads/paths
- **#00AF26** - Walkable areas
