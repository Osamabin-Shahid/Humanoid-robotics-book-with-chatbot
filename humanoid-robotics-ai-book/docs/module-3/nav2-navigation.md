---
sidebar_position: 3
---

# Chapter 3: Nav2 for Humanoid Navigation

## Introduction to Nav2 as the ROS 2 Navigation Framework

Navigation2 (Nav2) is the official ROS 2 navigation framework that provides a comprehensive set of tools, libraries, and applications for robot navigation. Designed as the successor to ROS 1's navigation stack, Nav2 offers a more robust, flexible, and performant solution for autonomous robot navigation, with specific capabilities that are particularly relevant for humanoid robots.

### The Evolution of ROS Navigation

Nav2 represents a significant evolution from the ROS 1 navigation stack with several key improvements:

- **Modern Architecture**: Built from the ground up for ROS 2 with improved modularity and maintainability
- **Enhanced Performance**: Optimized for real-time performance with better memory management and reduced latency
- **Improved Robustness**: Better error handling, recovery behaviors, and system resilience
- **Advanced Features**: Support for more sophisticated navigation behaviors and planning algorithms

### Core Components of Nav2

The Nav2 framework consists of several key components that work together to provide complete navigation capabilities:

- **Planners**: Global and local path planners that compute navigation paths
- **Controllers**: Trajectory controllers that execute navigation commands
- **Recovery Behaviors**: System behaviors to recover from navigation failures
- **Lifecycle Management**: Proper lifecycle state management for navigation components
- **Behavior Trees**: Flexible execution of complex navigation behaviors

### Nav2 for Humanoid Robots

For humanoid robots specifically, Nav2 provides unique capabilities that address the challenges of bipedal navigation:

- **Custom Controller Support**: Ability to integrate with humanoid-specific locomotion controllers
- **Stability-Aware Planning**: Path planning that considers balance and stability requirements
- **Human-Scale Navigation**: Navigation at human scale with appropriate speed and safety parameters
- **Social Navigation**: Capabilities for navigating in human environments with social awareness

## Global vs Local Planning

Navigation in Nav2 is divided into two complementary planning processes: global planning and local planning. Understanding the distinction between these two approaches is crucial for effective navigation, especially for humanoid robots that must balance path optimality with stability and safety.

### Global Planning

Global planning is responsible for computing a high-level, optimal path from the robot's current position to the goal location. The global planner:

- **Considers the entire map**: Uses a complete representation of the known environment
- **Computes optimal paths**: Finds the most efficient route based on cost maps and constraints
- **Generates long-term trajectories**: Creates path segments that span significant distances
- **Updates infrequently**: Recomputes only when significant environmental changes occur

In Nav2, global planners typically use algorithms like A* or Dijkstra's algorithm to find optimal paths while considering static obstacles and cost maps that represent areas of higher traversal cost.

### Local Planning

Local planning focuses on immediate navigation decisions and obstacle avoidance in the robot's immediate vicinity:

- **Considers immediate surroundings**: Focuses on a small area around the robot
- **Real-time obstacle avoidance**: Responds to dynamic obstacles not present in the global map
- **Generates executable trajectories**: Creates specific velocity commands for robot controllers
- **Updates frequently**: Recomputes at high frequency (typically 10-20 Hz) to respond to changes

Local planners in Nav2 often use methods like Trajectory Rollout or Dynamic Window Approach (DWA) to generate and evaluate potential local trajectories.

### Coordination Between Global and Local Planners

The interaction between global and local planners is carefully coordinated:

1. **Path Following**: The local planner follows the global path while making immediate adjustments
2. **Recovery Behaviors**: If the local planner cannot find a clear path, recovery behaviors are triggered
3. **Replanning**: The global planner may recompute the path if significant obstacles are encountered
4. **Feedback Loop**: The local planner provides feedback about actual progress to the global planner

### Humanoid-Specific Considerations

For humanoid robots, both global and local planning require special considerations:

**Global Planning for Humanoids**:
- **Stability constraints**: Paths must consider the robot's balance and stability requirements
- **Step planning**: Consideration of where the robot can safely place its feet
- **Dynamic constraints**: Incorporation of bipedal dynamics into path planning
- **Safety margins**: Larger safety zones to account for balance recovery needs

**Local Planning for Humanoids**:
- **Balance maintenance**: Local trajectories must maintain the robot's center of mass
- **Step-by-step navigation**: Consideration of individual steps rather than continuous motion
- **Recovery actions**: Ability to execute balance recovery behaviors when needed
- **Human-aware navigation**: Local adjustments that consider human safety and comfort

## Costmaps and Obstacle Avoidance

Costmaps are a fundamental concept in Nav2 that represent the environment as a grid of values indicating the cost of traversing each area. These costmaps are essential for both global and local planning, enabling robots to navigate safely around obstacles while considering various environmental factors.

### Understanding Costmaps

Costmaps provide a spatial representation of the environment where:

- **Free Space**: Areas with low cost values where navigation is preferred
- **Obstacles**: Areas with high cost values indicating impassable regions
- **Inflated Obstacles**: Areas around obstacles with increasing cost values to provide safety margins
- **Special Regions**: Areas with specific cost values for different types of terrain or constraints

### Types of Costmaps

Nav2 typically uses two main types of costmaps:

**Static Costmap**:
- Based on known map information
- Contains permanent obstacles and static features
- Updated only when the underlying map changes
- Used primarily by the global planner

**Local Costmap**:
- Based on sensor data from the robot's immediate environment
- Contains dynamic obstacles and real-time environmental information
- Continuously updated as the robot moves and sensors detect changes
- Used primarily by the local planner

### Costmap Layers

Costmaps in Nav2 are built using multiple layers that combine to create the final costmap:

- **Static Layer**: Incorporates the static map information
- **Obstacle Layer**: Processes sensor data to detect and represent obstacles
- **Inflation Layer**: Expands obstacles to create safety margins
- **Voxel Layer**: Handles 3D obstacle information for complex environments
- **Range Sensor Layer**: Processes data from range sensors like sonars

### Obstacle Avoidance Strategies

Nav2 implements sophisticated obstacle avoidance through:

- **Cost Propagation**: Spreading cost values from obstacles to surrounding areas
- **Inflation Parameters**: Configurable parameters to control safety margin size
- **Dynamic Obstacle Handling**: Processing of moving obstacles detected by sensors
- **Clearing Mechanisms**: Removing obstacle data that is no longer detected

### Humanoid-Specific Costmap Considerations

For humanoid robots, costmaps require special adaptations:

**Stability-Aware Costmaps**:
- Consideration of terrain stability and surface properties
- Different cost values for surfaces suitable for bipedal locomotion
- Incorporation of balance and stability constraints into cost calculations

**Step-Aware Costmaps**:
- Cost evaluation based on step placement feasibility
- Consideration of foot placement requirements
- Integration with humanoid step planning algorithms

**Social Costmaps**:
- Cost values that consider human comfort zones
- Areas with higher costs near humans to maintain respectful distances
- Dynamic adjustment based on human behavior and social context

### Costmap Configuration for Humanoids

Configuring costmaps for humanoid robots involves special parameters:

- **Inflation Radius**: Adjusted for humanoid safety requirements
- **Robot Footprint**: Accurate representation of humanoid base dimensions
- **Cost Scaling**: Adjusted for stability and balance considerations
- **Update Frequency**: Optimized for humanoid reaction times

## Differences Between Wheeled and Bipedal Navigation

Navigation for humanoid robots differs significantly from traditional wheeled robot navigation due to the fundamental differences in locomotion, stability, and environmental interaction. Understanding these differences is crucial for implementing effective navigation systems for bipedal robots.

### Kinematic Differences

**Wheeled Robots**:
- **Continuous Motion**: Can move in any direction without discrete steps
- **Stable Base**: Maintains stability through contact with wheels
- **Simple Dynamics**: Relatively simple kinematic model with predictable motion
- **Surface Independence**: Can navigate on most flat surfaces with minimal consideration for texture

**Bipedal Robots**:
- **Discrete Motion**: Must navigate by taking individual steps
- **Dynamic Stability**: Requires active balance control during locomotion
- **Complex Dynamics**: Complex kinematic model with multiple degrees of freedom
- **Surface Dependency**: Requires careful consideration of surface properties for foot placement

### Path Planning Considerations

**Wheeled Navigation**:
- **Smooth Paths**: Can follow smooth, curved paths with continuous motion
- **Point-to-Point**: Direct navigation between waypoints is typically feasible
- **Simple Obstacle Avoidance**: Can maneuver around obstacles with simple trajectory adjustments
- **Predictable Motion**: Motion is predictable and controllable with simple control models

**Bipedal Navigation**:
- **Step-Aware Paths**: Paths must consider where feet can be safely placed
- **Sequential Navigation**: Must navigate through a sequence of stable poses
- **Complex Obstacle Avoidance**: Requires careful planning of step sequences around obstacles
- **Balance-Constrained**: Path planning must consider balance and stability constraints

### Stability and Balance Requirements

**Wheeled Robots**:
- **Static Stability**: Maintains stability through geometric design
- **Low Center of Mass**: Typically have low center of mass for inherent stability
- **Minimal Balance Control**: Requires minimal active balance control
- **Recovery from Disturbance**: Can recover from disturbances with simple control adjustments

**Bipedal Robots**:
- **Dynamic Stability**: Requires continuous balance control throughout locomotion
- **High Center of Mass**: Higher center of mass requiring active balance control
- **Complex Balance Control**: Requires sophisticated balance control algorithms
- **Recovery from Disturbance**: Needs complex recovery behaviors to maintain balance

### Environmental Interaction

**Wheeled Robots**:
- **Minimal Interaction**: Wheels interact minimally with environment
- **Surface Tolerance**: Can operate on various surfaces with similar performance
- **Obstacle Interaction**: Can push through or go around most obstacles
- **Ground Clearance**: Minimal ground clearance requirements

**Bipedal Robots**:
- **Active Interaction**: Feet actively interact with ground surface
- **Surface Sensitivity**: Performance highly dependent on surface properties
- **Obstacle Negotiation**: Must carefully navigate around or over obstacles
- **Ground Requirements**: Requires appropriate ground clearance and step heights

### Navigation Algorithm Adaptations

To accommodate these differences, Nav2 for humanoid robots requires several adaptations:

**Step Planning Integration**:
- Path planning algorithms must consider step placement feasibility
- Integration with humanoid step planning algorithms
- Consideration of foot placement constraints in path planning

**Balance-Aware Navigation**:
- Incorporation of balance constraints into costmaps
- Integration with balance control systems
- Consideration of center of mass during navigation

**Humanoid-Specific Recovery Behaviors**:
- Balance recovery behaviors for bipedal robots
- Fall prevention and recovery strategies
- Humanoid-specific obstacle negotiation strategies

### Control Integration

**Wheeled Control**:
- Direct velocity control through wheel actuators
- Simple mapping from planned trajectories to wheel commands
- Minimal feedback from environment needed for stability

**Bipedal Control**:
- Complex mapping from planned paths to joint commands
- Integration with humanoid locomotion controllers
- Continuous feedback from balance and environment sensors
- Coordination between multiple control systems (balance, navigation, locomotion)

## Balance, Stability, and Step-Aware Path Planning

Navigation for humanoid robots must carefully consider the fundamental challenges of maintaining balance and stability while moving through the environment. This requires specialized approaches to path planning that are fundamentally different from those used for wheeled robots.

### Balance and Stability Fundamentals

Humanoid robots face unique challenges in maintaining balance and stability:

**Center of Mass Management**:
- Humanoid robots have a high center of mass that requires active control
- The center of mass must be kept within the support polygon defined by foot contact points
- Balance control must be maintained throughout the entire navigation process

**Support Polygon Considerations**:
- During single support (one foot on ground), the center of mass must be directly over the supporting foot
- During double support (both feet on ground), the center of mass can be anywhere between the feet
- Step transitions require careful coordination to maintain balance throughout

**Dynamic Balance Requirements**:
- Balance must be maintained not just statically but dynamically during motion
- The robot must continuously adjust its posture to compensate for motion-induced forces
- External disturbances require immediate balance recovery responses

### Step-Aware Path Planning

Traditional path planning approaches are insufficient for humanoid robots due to their discrete step-based locomotion:

**Footstep Planning**:
- Paths must be planned as sequences of viable footstep locations
- Each step must provide a stable support configuration
- Footstep sequences must ensure continuous stability throughout navigation

**Stability Criteria**:
- Each potential footstep location must satisfy stability constraints
- The sequence of steps must maintain dynamic balance throughout
- Step timing must be coordinated with balance control systems

**Step Placement Constraints**:
- Surface properties must be suitable for foot contact
- Step spacing must be within the robot's physical capabilities
- Obstacles must be considered at foot level, not just at body level

### Integration with Navigation Systems

Step-aware path planning must be integrated with the broader navigation system:

**Multi-Layer Planning**:
- High-level path planning considering general navigation goals
- Mid-level step planning ensuring stability constraints
- Low-level balance control maintaining stability during execution

**Real-time Adaptation**:
- Step plans must be adaptable to environmental changes
- Balance recovery behaviors must be integrated with navigation
- Dynamic obstacle avoidance must consider step planning constraints

### Balance-Aware Costmaps

Specialized costmaps are needed to incorporate balance and stability considerations:

**Stability Costmaps**:
- Cost values based on the stability of potential foot placements
- Incorporation of terrain properties relevant to balance
- Consideration of surface friction and stability

**Step Feasibility Costmaps**:
- Cost values based on the feasibility of step sequences
- Consideration of robot kinematic constraints
- Integration of balance margin requirements

### Stability-Aware Navigation Behaviors

Navigation behaviors must incorporate stability considerations:

**Safe Navigation**:
- Maintaining larger safety margins for balance recovery
- Slower navigation speeds to allow for balance adjustments
- Preferred paths that offer better stability options

**Recovery Behaviors**:
- Integration of balance recovery into navigation recovery
- Step adjustment behaviors for obstacle avoidance
- Fall prevention strategies during navigation

### Humanoid-Specific Path Planning Algorithms

Specialized algorithms are required for humanoid navigation:

**Footstep-Enabled Planners**:
- Adaptation of traditional planners to consider footstep constraints
- Integration of balance constraints into path optimization
- Consideration of step sequence feasibility in planning

**Stability-Optimized Paths**:
- Paths optimized for stability rather than just distance
- Consideration of balance recovery options along the path
- Integration of dynamic balance requirements into path selection

These specialized approaches ensure that humanoid robots can navigate safely and effectively while maintaining the dynamic balance required for bipedal locomotion.

## Mapping Nav2 Outputs to Humanoid Motion Controllers

The navigation commands generated by Nav2 must be translated into appropriate motion commands for humanoid robot controllers. This mapping is complex due to the fundamental differences between traditional navigation outputs and humanoid robot motion requirements.

### Traditional Navigation vs Humanoid Motion

**Standard Navigation Output**:
- Velocity commands (linear and angular velocities)
- Path waypoints in global coordinate frame
- Continuous motion trajectories
- Simple kinematic models

**Humanoid Motion Requirements**:
- Joint position/velocity commands
- Step planning and foot placement commands
- Balance control integration
- Complex kinematic models with multiple degrees of freedom

### High-Level Navigation to Step Planning

The translation from Nav2 outputs to humanoid motion involves several intermediate steps:

**Path Discretization**:
- Converting continuous paths into discrete step locations
- Determining appropriate step timing and sequencing
- Ensuring step feasibility within robot kinematic constraints

**Step Planning Integration**:
- Coordinating with humanoid-specific step planning algorithms
- Ensuring each planned step maintains stability
- Integrating balance constraints into step planning

### Motion Control Architecture

A typical architecture for mapping Nav2 to humanoid motion includes:

**Navigation Layer**:
- Standard Nav2 components (global planner, local planner, controllers)
- High-level path planning and obstacle avoidance
- Behavior trees for complex navigation tasks

**Step Planning Layer**:
- Conversion of navigation goals to footstep plans
- Balance-aware step sequencing
- Integration with humanoid kinematics

**Motion Control Layer**:
- Balance control systems
- Joint trajectory generation
- Real-time motion execution

### Control Integration Strategies

Several strategies are used to integrate Nav2 outputs with humanoid controllers:

**Hierarchical Control**:
- High-level navigation commands guide low-level motion
- Motion controllers execute detailed joint movements
- Coordination between balance and navigation systems

**Feedback Integration**:
- Motion execution feedback to navigation system
- Balance state feedback to navigation planning
- Real-time adjustment based on execution success

### Humanoid-Specific Navigation Interfaces

Specialized interfaces are needed for humanoid navigation:

**Step Command Interface**:
- Direct interface for sending step planning commands
- Integration with humanoid-specific step planning algorithms
- Coordination of multiple step planning phases

**Balance Integration Interface**:
- Interface for coordinating balance and navigation
- Real-time balance state sharing
- Emergency balance recovery coordination

### Implementation Considerations

When implementing Nav2-to-humanoid motion mapping:

**Timing Coordination**:
- Synchronization between navigation and motion control frequencies
- Appropriate timing for step execution and balance updates
- Handling of delays and communication latencies

**Safety Integration**:
- Emergency stop capabilities integrated with navigation
- Balance failure recovery in navigation context
- Safe motion termination procedures

**Performance Optimization**:
- Efficient computation of step plans from navigation goals
- Real-time capability for dynamic environment adaptation
- Minimization of computational overhead

This mapping layer is critical for enabling humanoid robots to effectively utilize Nav2's navigation capabilities while maintaining the complex control requirements of bipedal locomotion.

## Nav2 Architecture: Conceptual Overview

The Nav2 architecture for humanoid robots integrates navigation planning with the complex requirements of bipedal locomotion. Understanding this architecture helps in implementing effective navigation systems for humanoid robots.

### Core Architecture Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Nav2 for Humanoid Robots                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  Global        │  │  Local          │  │  Humanoid Motion       │  │
│  │  Planner       │  │  Planner        │  │  Control              │  │
│  │                │  │                 │  │                       │  │
│  │  - A*, Dijkstra│  │  - DWA, TEB    │  │  - Balance Control    │  │
│  │  - Path Planning│  │  - Trajectory  │  │  - Step Planning      │  │
│  │  - Costmaps    │  │    Generation   │  │  - Joint Control      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   Costmap   │    │   Behavior  │    │   Recovery  │
   │   System    │    │   Tree      │    │   System    │
   │             │    │   Engine    │    │             │
   │  - Static   │    │  - Navigation│    │  - Balance │
   │    Layer    │    │    Behaviors│    │    Recovery │
   │  - Obstacle │    │  - Recovery│      │  - Path    │
   │    Layer    │    │    Behaviors│      │    Recovery │
   │  - Inflation│    │  - Control │      │             │
   │    Layer    │    │    Actions  │      │             │
   └─────────────┘    └─────────────┘      └─────────────┘
```

### Humanoid-Specific Navigation Flow

The navigation flow for humanoid robots includes additional layers to handle bipedal locomotion:

```
High-Level Goal → Global Path Planning → Step Planning → Motion Execution
      ↓                    ↓                   ↓              ↓
Navigation Goal    Optimal path for      Feasible step    Joint position/
                  humanoid navigation     sequence for     velocity commands
                                        bipedal stability
```

### Integration Architecture

Nav2 for humanoid robots integrates multiple systems:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Navigation Integration Layer                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │   Nav2       │    │   Step       │    │   Balance    │            │
│  │   System     │◄──►│   Planning   │◄──►│   Control    │            │
│  │              │    │   System     │    │   System     │            │
│  │  - Global    │    │  - Footstep  │    │  - Stability│            │
│  │    Planner   │    │    Planning  │    │    Control  │            │
│  │  - Local     │    │  - Step      │    │  - Fall     │            │
│  │    Planner   │    │    Sequencing│    │    Prevention│            │
│  └──────────────┘    └──────────────┘    └──────────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Integration Points

The architecture emphasizes several key integration points:

- **Path to Step Translation**: Converting navigation paths to humanoid-appropriate step sequences
- **Balance-Aware Planning**: Ensuring all navigation plans consider balance constraints
- **Recovery Behaviors**: Coordinated recovery for both navigation and balance failures
- **Real-time Adaptation**: Continuous adjustment based on balance and environmental feedback

## Chapter Summary and Learning Outcomes

After completing this chapter, you should now understand:

- The fundamental architecture and components of the Nav2 navigation framework
- The critical differences between global and local planning in robot navigation
- How costmaps represent environmental information for navigation and obstacle avoidance
- The significant differences between wheeled and bipedal navigation requirements
- The specialized challenges of balance, stability, and step-aware path planning for humanoid robots
- How Nav2 outputs are mapped to humanoid motion controllers and integrated with balance systems
- The architectural considerations for implementing Nav2 with humanoid robots
- The importance of balance-aware navigation for safe humanoid locomotion

These concepts demonstrate how Nav2 provides a comprehensive navigation solution specifically adapted for the unique requirements of humanoid robots, integrating path planning, obstacle avoidance, and balance control into a unified framework.

## Next Steps

This concludes Module 3: The AI-Robot Brain (NVIDIA Isaac™). You now have a comprehensive understanding of how NVIDIA Isaac technologies (Isaac Sim, Isaac ROS) and Nav2 work together to create the cognitive and navigation capabilities of humanoid robots. These technologies form the "brain" of the humanoid robot, enabling it to perceive, understand, and navigate its environment intelligently.

As you continue your journey in Physical AI and Humanoid Robotics, consider how these three modules work together:
- Module 1 (ROS 2) provides the nervous system for robot communication and control
- Module 2 (Digital Twins) provides simulation and validation capabilities
- Module 3 (AI-Robot Brain) provides perception, cognition, and navigation capabilities

## Cross-Module Connections

This chapter builds upon concepts introduced in previous modules:

**Connection to Module 1 (ROS 2)**: Nav2 is built as the official ROS 2 navigation framework, utilizing the ROS 2 middleware concepts you learned in Module 1. All Nav2 components are implemented as ROS 2 nodes with proper lifecycle management, using ROS 2 topics, services, and parameters for communication and configuration.

**Connection to Module 2 (Digital Twins)**: The navigation capabilities we've discussed can be developed and tested in the simulation environments from Module 2. Nav2 can operate in both simulated environments (like those created with Isaac Sim) and real-world deployments, providing a consistent navigation framework across simulation and reality.

These connections demonstrate how Nav2 integrates with the broader humanoid robot system, connecting the foundational ROS 2 concepts (Module 1) with the simulation capabilities (Module 2) to create comprehensive navigation solutions for humanoid robots.

## Nav2 Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Nav2 for Humanoids                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   High-Level│    │  Nav2       │    │  Humanoid   │          │
│  │   Goals     │◄──►│  Navigation │◄──►│  Motion     │          │
│  │             │    │  System     │    │  Control    │          │
│  │  - Waypoints│    │  - Global   │    │  - Balance  │          │
│  │  - Maps     │    │    Planner  │    │  - Step    │          │
│  │  - Safety   │    │  - Local    │    │    Planning │          │
│  │  - Social   │    │    Planner   │    │  - Locomotion│         │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

## Cross-References to Related Concepts

This chapter's concepts connect with other chapters in Module 3:

- **Chapter 1 (Isaac Sim)**: Navigation behaviors can be developed and tested in Isaac Sim environments before real-world deployment
- **Chapter 2 (Isaac ROS)**: Nav2 navigation decisions are informed by Isaac ROS perception outputs
- **Module 2**: Nav2 can operate in both simulated environments and real-world deployments

## Summary and Next Steps

This chapter concluded Module 3 by exploring Navigation2 (Nav2), the ROS 2 navigation framework that forms the third component of the AI-Robot brain. You learned about global and local planning, costmaps, humanoid-specific navigation considerations, and how Nav2 integrates with humanoid motion controllers.

This completes Module 3: The AI-Robot Brain (NVIDIA Isaac™). You now have a comprehensive understanding of how Isaac Sim, Isaac ROS, and Nav2 work together to create the cognitive and navigation capabilities of humanoid robots.