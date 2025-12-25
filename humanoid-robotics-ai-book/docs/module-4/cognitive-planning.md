---
sidebar_position: 2
---

# Chapter 2: Cognitive Planning with LLMs

## Learning Objectives
By the end of this chapter, you will be able to:
- Define Vision-Language-Action (VLA) systems in robotics
- Explain how LLMs convert high-level goals into step-by-step task plans
- Describe task decomposition with practical examples
- Understand prompt grounding and hallucination mitigation in robotics contexts
- Identify integration patterns between LLM planners and ROS 2 nodes
- Apply decision-flow diagrams and failure-handling strategies

## Introduction: Vision-Language-Action (VLA) Systems in Robotics

Vision-Language-Action (VLA) systems represent a paradigm shift in robotics, where large language models serve as cognitive planners that can interpret high-level goals and generate executable action sequences. Unlike traditional robotics approaches that require pre-programmed behaviors for specific tasks, VLA systems enable robots to understand natural language commands and autonomously plan complex multi-step tasks.

In humanoid robotics, VLA systems bridge the gap between human intention and robotic execution by leveraging the reasoning capabilities of large language models. When a user says "Please clean the living room," a VLA system can decompose this high-level goal into specific actions: identifying objects that need cleaning, navigating to those objects, manipulating cleaning tools, and executing the appropriate cleaning procedures.

### Core Components of VLA Systems

VLA systems integrate three critical modalities:

1. **Vision**: Perception of the environment through cameras, LIDAR, and other sensors
2. **Language**: Natural language understanding and generation capabilities
3. **Action**: Execution of physical or digital tasks through robotic systems

These components work in concert to create an intelligent system that can perceive its environment, understand human commands, and execute appropriate actions.

### The Cognitive Planning Process

The cognitive planning process in VLA systems follows a structured pipeline:

```
High-Level Goal → LLM Reasoning → Task Decomposition → Action Sequencing → Execution
```

This process enables humanoid robots to handle novel situations and adapt their behavior based on environmental context and changing requirements.

## How LLMs Convert High-Level Goals to Step-by-Step Task Plans

Large Language Models serve as cognitive planners by leveraging their training on vast amounts of text data to understand task relationships, common-sense reasoning, and procedural knowledge. When presented with a high-level goal, LLMs can generate detailed execution plans that account for environmental constraints and task dependencies.

### Planning Architecture

The LLM-based planning process involves several key steps:

1. **Goal Interpretation**: Understanding the user's high-level objective and any constraints
2. **Context Integration**: Incorporating environmental information and current robot state
3. **Task Decomposition**: Breaking down complex goals into manageable subtasks
4. **Action Sequencing**: Ordering subtasks based on dependencies and requirements
5. **Resource Allocation**: Assigning appropriate robotic capabilities to each subtask
6. **Monitoring Preparation**: Planning for progress tracking and error recovery

### Example: "Clean the Living Room"

When an LLM receives the command "Clean the living room," it performs the following cognitive planning:

```
Goal: "Clean the living room"

1. Identify cleaning targets:
   - Surface objects that need removal
   - Floor areas that need cleaning
   - Dust accumulation points

2. Prioritize tasks:
   - Remove objects before cleaning floor
   - Clean from top to bottom (dusting before sweeping)
   - Handle fragile items carefully

3. Generate action sequence:
   - Navigate to living room
   - Scan for objects requiring action
   - Pick up items that don't belong
   - Move to storage area
   - Return to living room
   - Navigate to dusting locations
   - Execute dusting actions
   - Navigate to floor cleaning locations
   - Execute floor cleaning actions
```

### Context-Aware Planning

Effective LLM-based planning incorporates environmental context:

- **Current State**: Robot location, battery level, available tools
- **Environmental State**: Room layout, object positions, detected obstacles
- **Temporal Constraints**: Time limits, scheduling requirements
- **Safety Constraints**: Human presence, fragile objects, restricted areas

## Task Decomposition with Examples

Task decomposition is the process of breaking complex goals into smaller, executable subtasks. This is crucial for humanoid robots as it transforms abstract goals into concrete actions that can be executed through ROS 2 services and actions.

### Example 1: "Set the Dining Table for Four"

High-level goal: "Set the dining table for four"

**Decomposed Task Plan:**
```
1. Navigate to dining table
2. Count chairs around table (verify 4 seats available)
3. For each seat:
   a. Approach seat location
   b. Place plate in front of chair
   c. Place fork on left side of plate
   d. Place knife and spoon on right side of plate
   e. Place glass above the knife
   f. Place napkin to the left of the fork
4. Verify all settings are complete
5. Report completion to user
```

### Example 2: "Help the Elderly Person Get Dressed"

High-level goal: "Help the elderly person get dressed"

**Decomposed Task Plan:**
```
1. Navigate to person
2. Identify appropriate clothing based on weather/occasion
3. Ensure privacy (close curtains, doors if needed)
4. Assist with upper body clothing:
   a. Help person put on shirt
   b. Adjust sleeves and collar
   c. Fasten buttons/zippers if needed
5. Assist with lower body clothing:
   a. Help person put on pants
   b. Adjust waistband and length
   c. Fasten buttons/zippers if needed
6. Assist with footwear:
   a. Help person put on socks
   b. Help person put on shoes
   c. Secure laces or fasteners
7. Verify comfort and mobility
8. Report completion to caregiver
```

### Example 3: "Organize the Bookshelf"

High-level goal: "Organize the bookshelf"

**Decomposed Task Plan:**
```
1. Navigate to bookshelf
2. Scan and catalog all books currently on shelf
3. Determine organization criteria (by genre, author, size, etc.)
4. Plan new arrangement based on criteria
5. Remove all books from shelf systematically
6. Clean shelf surface
7. Place books in new arrangement:
   a. Start with bottom shelf
   b. Place books according to organization plan
   c. Ensure stable stacking
8. Verify organization matches plan
9. Report completion
```

## Prompt Grounding and Hallucination Mitigation

One of the critical challenges in using LLMs for robotic planning is ensuring that the generated plans are grounded in reality and do not contain hallucinations that could lead to unsafe or impossible robot behaviors.

### Prompt Grounding Strategies

**Environmental Context Injection:**
```
Current Environment: Kitchen
Robot Capabilities:
- Arm reach: 1.2m
- Gripper: Can grasp objects 2-15cm wide
- Navigation: Can move to any accessible location

Goal: "Get me a snack"
Grounded Response:
1. Navigate to kitchen counter (accessible location)
2. Identify snack items within reach (apples, cookies on counter)
3. Grasp selected snack item
4. Navigate to user location
5. Present snack to user
```

**Capability Constraints:**
Always include the robot's physical and functional limitations in prompts to prevent impossible action generation.

**Sensor Feedback Integration:**
Use real-time sensor data to update the LLM's understanding of the current state before generating plans.

### Hallucination Mitigation Techniques

**Reality Checking:**
- Validate proposed actions against known robot capabilities
- Cross-reference with environmental sensor data
- Verify object existence and accessibility before planning

**Plan Verification:**
- Implement sanity checks on generated plans
- Validate action sequences for logical consistency
- Check for potential safety violations

**Iterative Refinement:**
- Generate initial plan with LLM
- Apply reality constraints
- Request refined plan if inconsistencies exist
- Repeat until plan is feasible

### Safety Constraints

LLM-generated plans must incorporate safety protocols:

- **Physical Safety**: Avoid actions that could harm humans or damage property
- **Operational Safety**: Respect robot operational limits and constraints
- **Social Safety**: Follow appropriate social protocols and privacy considerations
- **Environmental Safety**: Consider environmental factors and potential hazards

## Integration Patterns Between LLM Planners and ROS 2 Nodes

The integration of LLM cognitive planners with ROS 2 systems requires careful architectural design to ensure reliable communication, proper error handling, and appropriate feedback loops.

### Architecture Pattern 1: Centralized Planning Node

```
[LLM Planner Node] ←→ [ROS 2 Action Servers] ←→ [Robot Hardware]
       ↓
[Plan Execution Monitor]
       ↓
[Feedback Collection Node]
```

In this pattern, a dedicated LLM planner node receives high-level goals, generates plans, and coordinates with various ROS 2 action servers to execute the plan.

### Architecture Pattern 2: Hierarchical Planning

```
High-Level LLM Planner
        ↓
Mid-Level Task Decomposer
        ↓
Low-Level Action Executors
```

This pattern separates planning concerns by level of abstraction, allowing for more sophisticated reasoning while maintaining execution efficiency.

### ROS 2 Message Types for LLM Integration

**Plan Request Messages:**
```
message PlanRequest {
  string goal_description;      // Natural language goal
  string context_description;   // Environmental context
  int32 priority;              // Task priority level
  float timeout;               // Maximum planning time
}
```

**Plan Response Messages:**
```
message PlanResponse {
  repeated ActionStep steps;    // Sequence of actions
  float confidence_score;      // LLM confidence in plan
  string reasoning_trace;      // Explanation of plan
  string status;               // Success/Failed/Partial
}
```

**Action Step Messages:**
```
message ActionStep {
  string action_type;          // Type of action (NAVIGATE, GRASP, etc.)
  string parameters;           // Action-specific parameters
  string ros_service_name;     // Target ROS service
  float estimated_duration;    // Expected execution time
  string preconditions;        // Required preconditions
  string effects;              // Expected outcomes
}
```

### Communication Protocols

**Synchronous Planning:**
- LLM planner receives goal
- Generates complete plan
- Returns plan to requester
- Plan is executed by separate execution system

**Asynchronous Planning:**
- LLM planner receives goal and returns immediately
- Generates plan in background
- Publishes plan when complete
- Execution system subscribes to plan updates

**Reactive Planning:**
- LLM planner continuously monitors environment
- Updates plan based on new information
- Adapts to changing conditions in real-time

## Decision-Flow Diagrams and Failure-Handling Strategies

Effective VLA systems must include robust decision-making processes and failure-handling strategies to operate reliably in dynamic environments.

### Decision-Flow Diagram for Task Planning

```
Start: High-Level Goal Received
        ↓
[Goal Feasibility Check]
        ↓
┌─────────────────┐
│  Feasible?      │ ←─┐
└─────────────────┘   │
        ↓Yes          │No
[Context Gathering]    │
        ↓              │
[Task Decomposition]   │
        ↓              │
[Action Sequencing]    │
        ↓              │
[Resource Validation]  │
        ↓              │
┌─────────────────┐    │
│  Valid Plan?    │ ←──┘
└─────────────────┘
        ↓Yes
[Plan Execution]
        ↓
[Progress Monitoring]
        ↓
┌─────────────────┐
│  Task Complete? │
└─────────────────┘
        ↓No
[Failure Analysis]
        ↓
[Recovery Strategy]
        ↓
[Plan Revision]
        ↓
Back to Execution
```

### Failure-Handling Strategies

**Recovery by Retrying:**
- For transient failures (object not found, navigation blocked)
- Retry with slight parameter variations
- Increase search area or try alternative approaches

**Recovery by Substitution:**
- When primary object/action unavailable
- Identify and use functionally equivalent alternatives
- Update plan to incorporate substitutions

**Recovery by Abstraction:**
- When detailed plan fails
- Fall back to higher-level strategy
- Regenerate plan with different approach

**Recovery by Delegation:**
- When robot cannot complete task
- Request human assistance
- Provide clear explanation of failure

### Error Taxonomy for LLM-Driven Robotics

**Planning Errors:**
- Impossible goals
- Inconsistent plans
- Resource conflicts
- Temporal violations

**Execution Errors:**
- Physical constraint violations
- Sensor inaccuracies
- Environmental changes
- Hardware failures

**Communication Errors:**
- Message timeouts
- Data corruption
- Service unavailability
- Network disruptions

**Safety Errors:**
- Potential harm to humans
- Property damage risk
- Privacy violations
- Protocol breaches

## Chapter Summary

This chapter has provided a comprehensive overview of cognitive planning with LLMs for humanoid robots, covering:

1. **VLA Systems Understanding**: Vision-Language-Action systems that integrate perception, language understanding, and action execution to create intelligent robotic systems.

2. **LLM Planning Capabilities**: How large language models serve as cognitive planners that convert high-level goals into executable task sequences.

3. **Task Decomposition**: Techniques for breaking down complex goals into manageable subtasks that align with robot capabilities.

4. **Safety and Grounding**: Methods for ensuring LLM-generated plans are grounded in reality and include hallucination mitigation strategies.

5. **ROS 2 Integration**: Proper integration patterns that ensure reliable communication between LLM planners and robotic systems.

6. **Failure Handling**: Robust decision-making and recovery strategies essential for reliable robot operation.

7. **Practical Examples**: Real-world scenarios demonstrating task decomposition and planning for various robotic tasks.

## Next Steps

To further develop your understanding of cognitive planning with LLMs:

1. **Hands-On Practice**: Implement a simple LLM-based planner for a basic robotic task using ROS 2
2. **Advanced Topics**: Explore reinforcement learning approaches to improve planning efficiency
3. **Module Progression**: Continue to [Chapter 3: Capstone – The Autonomous Humanoid](./autonomous-humanoid.md) to see how voice interfaces and cognitive planning work together in a complete autonomous system
4. **Cross-Module Learning**: Apply cognitive planning concepts to simulation environments in Module 2 for safe testing

## Learning Outcomes

This chapter has covered the fundamental concepts of cognitive planning with LLMs for humanoid robots:

1. **VLA Systems Understanding**: Vision-Language-Action systems integrate perception, language understanding, and action execution to create intelligent robotic systems.

2. **LLM Planning Capabilities**: Large language models can serve as cognitive planners that convert high-level goals into executable task sequences.

3. **Task Decomposition**: Complex goals must be broken down into manageable subtasks that align with robot capabilities.

4. **Safety and Grounding**: LLM-generated plans must be grounded in reality and include hallucination mitigation strategies.

5. **ROS 2 Integration**: Proper integration patterns ensure reliable communication between LLM planners and robotic systems.

6. **Failure Handling**: Robust decision-making and recovery strategies are essential for reliable robot operation.

## Cross-Module Integration Notes

This chapter connects to other modules in the humanoid robotics curriculum:

- **Module 1 (ROS 2)**: LLM planners generate action sequences that execute as ROS 2 services and actions
- **Module 2 (Simulation)**: Cognitive planning can be tested and validated in simulated environments
- **Module 3 (Isaac)**: NVIDIA Isaac provides computational resources for running LLM inference on robots

The cognitive planning layer sits above the basic ROS 2 communication layer, orchestrating complex behaviors by generating appropriate sequences of ROS 2 commands based on high-level goals.

## Cross-Chapter References

This chapter connects to other chapters in Module 4:

- **Chapter 1 (Voice-to-Action)**: The cognitive planning system receives high-level goals from the voice-to-action interface described in Chapter 1, transforming natural language commands into executable plans
- **Chapter 3 (Autonomous Humanoid)**: The planning algorithms and integration patterns discussed here form the cognitive core of the autonomous humanoid system described in Chapter 3

For more information on how voice commands are processed and converted to structured intents, see [Chapter 1: Voice-to-Action Interfaces](./voice-to-action.md). For the complete autonomous system integrating voice, planning, and execution, see [Chapter 3: Capstone – The Autonomous Humanoid](./autonomous-humanoid.md).

## How This Fits in the Full Humanoid Stack

The cognitive planning system described in this chapter represents the reasoning and decision-making layer in the complete humanoid system:

- **Cognitive Layer**: This chapter provides the high-level reasoning capabilities that transform human goals into executable action sequences
- **Task Orchestration**: Decomposes complex goals into manageable subtasks that can be executed by the robot's action systems (Module 1)
- **Integration Hub**: Connects the voice input from Chapter 1 with the action execution systems, creating a complete pipeline from human intent to robot behavior
- **Autonomy Foundation**: Forms the core reasoning engine for the autonomous humanoid system (Chapter 3)

This chapter builds upon the voice processing capabilities from Chapter 1 and leverages the ROS 2 infrastructure from Module 1 to create intelligent, goal-driven robot behavior.

## Quality Assurance

This chapter has been developed following the quality standards for the Physical AI & Humanoid Robotics curriculum:

- **Technical Accuracy**: All concepts related to LLM cognitive planning, task decomposition, and VLA systems have been validated against current research and best practices
- **Conceptual Clarity**: Complex planning algorithms and integration patterns are explained with clear examples and practical scenarios
- **ROS 2 Integration**: All references to ROS 2 services and actions are consistent with the middleware concepts introduced in Module 1
- **Safety Considerations**: Proper attention has been given to hallucination mitigation and safety protocols in LLM-driven robotics
- **RAG Compatibility**: Content is structured with clear headings, consistent terminology, and conceptual explanations suitable for retrieval-augmented generation systems
- **Educational Alignment**: Learning objectives are clearly defined and aligned with the practical applications of cognitive planning in robotics