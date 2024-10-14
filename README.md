Optimal Sensor Placement in Sewer Systems
Authors: Thi Hai Duong Ninh, Nhu Cuong Do, Wei Zeng, Martin Francis Lambert.

This repository presents two optimization problems for determining optimal sensor placements in sewer systems. The problems aim to enhance monitoring efficiency by strategically minimizing the number of sensors and determining their best locations to meet specific requirements. The optimization tasks are implemented using Python.

Overview of Optimization Problems
  Minimizing the Number of Sensors:
      This problem focuses on finding the minimal number of sensors required to fully monitor the entire sewer system.

  Optimal Sensor Placement for a Given Number of Sensors:
      This problem is designed to identify the best sensor locations for a fixed number of sensors, tailored to specific investment phases or budget constraints.

Methodology
  The first step involves identifying covered and uncovered nodes associated with each potential sensor location. The implementation and results for this task can be found in the "FindDownstream_dependent_node" folder.

  Minimization of Sensors:
      The algorithm for minimizing the number of sensors has been applied to two sewer systems (named System 1 and System 2). The implementation and results for this task can be found in the "minimize_number_of_sensors" folder.

  Optimal Sensor Locations:
      The solution to the problem of finding the optimal sensor locations for given a specific number of sensors has been implemented for System 1. The relevant file is located in the "lengthcover" folder.

  Visualization
      Visualization scripts for both optimization problems are available in the "visualisation" folder. These scripts provide graphical representations of the sewer systems, sensor placements, and node coverage to help interpret the results.
  
Usage
To run the optimization codes, ensure you have the necessary Python dependencies installed.
